import logging
import time
from typing import cast

from core.app.app_queue_manager import AppQueueManager, PublishFrom
from core.app.apps.advanced_chat.app_config_manager import AdvancedChatAppConfig
from core.app.apps.base_app_runner import AppRunner
from core.app.entities.app_invoke_entities import (
    AdvancedChatAppGenerateEntity,
    InvokeFrom,
)
from core.app.entities.queue_entities import QueueStopEvent
from core.callback_handler.workflow_event_trigger_callback import WorkflowEventTriggerCallback
from core.moderation.base import ModerationException
from core.workflow.entities.node_entities import SystemVariable
from core.workflow.workflow_engine_manager import WorkflowEngineManager
from extensions.ext_database import db
from models.account import Account
from models.model import App, Conversation, EndUser, Message
from models.workflow import WorkflowRunTriggeredFrom

logger = logging.getLogger(__name__)


class AdvancedChatAppRunner(AppRunner):
    """
    AdvancedChat Application Runner
    """

    def run(self, application_generate_entity: AdvancedChatAppGenerateEntity,
            queue_manager: AppQueueManager,
            conversation: Conversation,
            message: Message) -> None:
        """
        Run application
        :param application_generate_entity: application generate entity
        :param queue_manager: application queue manager
        :param conversation: conversation
        :param message: message
        :return:
        """
        app_config = application_generate_entity.app_config
        app_config = cast(AdvancedChatAppConfig, app_config)

        app_record = db.session.query(App).filter(App.id == app_config.app_id).first()
        if not app_record:
            raise ValueError("App not found")

        workflow = WorkflowEngineManager().get_workflow(app_model=app_record, workflow_id=app_config.workflow_id)
        if not workflow:
            raise ValueError("Workflow not initialized")

        inputs = application_generate_entity.inputs
        query = application_generate_entity.query
        files = application_generate_entity.files

        # moderation
        if self.handle_input_moderation(
                queue_manager=queue_manager,
                app_record=app_record,
                app_generate_entity=application_generate_entity,
                inputs=inputs,
                query=query
        ):
            return

        # annotation reply
        if self.handle_annotation_reply(
                app_record=app_record,
                message=message,
                query=query,
                queue_manager=queue_manager,
                app_generate_entity=application_generate_entity
        ):
            return

        # fetch user
        if application_generate_entity.invoke_from in [InvokeFrom.DEBUGGER, InvokeFrom.EXPLORE]:
            user = db.session.query(Account).filter(Account.id == application_generate_entity.user_id).first()
        else:
            user = db.session.query(EndUser).filter(EndUser.id == application_generate_entity.user_id).first()

        # RUN WORKFLOW
        workflow_engine_manager = WorkflowEngineManager()
        result_generator = workflow_engine_manager.run_workflow(
            app_model=app_record,
            workflow=workflow,
            triggered_from=WorkflowRunTriggeredFrom.DEBUGGING
            if application_generate_entity.invoke_from == InvokeFrom.DEBUGGER else WorkflowRunTriggeredFrom.APP_RUN,
            user=user,
            user_inputs=inputs,
            system_inputs={
                SystemVariable.QUERY: query,
                SystemVariable.FILES: files,
                SystemVariable.CONVERSATION: conversation.id,
            },
            callbacks=[WorkflowEventTriggerCallback(queue_manager=queue_manager)]
        )

        for result in result_generator:
            # todo handle workflow and node event
            pass


    def handle_input_moderation(self, queue_manager: AppQueueManager,
                                app_record: App,
                                app_generate_entity: AdvancedChatAppGenerateEntity,
                                inputs: dict,
                                query: str) -> bool:
        """
        Handle input moderation
        :param queue_manager: application queue manager
        :param app_record: app record
        :param app_generate_entity: application generate entity
        :param inputs: inputs
        :param query: query
        :return:
        """
        try:
            # process sensitive_word_avoidance
            _, inputs, query = self.moderation_for_inputs(
                app_id=app_record.id,
                tenant_id=app_generate_entity.app_config.tenant_id,
                app_generate_entity=app_generate_entity,
                inputs=inputs,
                query=query,
            )
        except ModerationException as e:
            self._stream_output(
                queue_manager=queue_manager,
                text=str(e),
                stream=app_generate_entity.stream,
                stopped_by=QueueStopEvent.StopBy.INPUT_MODERATION
            )
            return True

        return False

    def handle_annotation_reply(self, app_record: App,
                                message: Message,
                                query: str,
                                queue_manager: AppQueueManager,
                                app_generate_entity: AdvancedChatAppGenerateEntity) -> bool:
        """
        Handle annotation reply
        :param app_record: app record
        :param message: message
        :param query: query
        :param queue_manager: application queue manager
        :param app_generate_entity: application generate entity
        """
        # annotation reply
        annotation_reply = self.query_app_annotations_to_reply(
            app_record=app_record,
            message=message,
            query=query,
            user_id=app_generate_entity.user_id,
            invoke_from=app_generate_entity.invoke_from
        )

        if annotation_reply:
            queue_manager.publish_annotation_reply(
                message_annotation_id=annotation_reply.id,
                pub_from=PublishFrom.APPLICATION_MANAGER
            )

            self._stream_output(
                queue_manager=queue_manager,
                text=annotation_reply.content,
                stream=app_generate_entity.stream,
                stopped_by=QueueStopEvent.StopBy.ANNOTATION_REPLY
            )
            return True

        return False

    def _stream_output(self, queue_manager: AppQueueManager,
                       text: str,
                       stream: bool,
                       stopped_by: QueueStopEvent.StopBy) -> None:
        """
        Direct output
        :param queue_manager: application queue manager
        :param text: text
        :param stream: stream
        :return:
        """
        if stream:
            index = 0
            for token in text:
                queue_manager.publish_text_chunk(token, PublishFrom.APPLICATION_MANAGER)
                index += 1
                time.sleep(0.01)

        queue_manager.publish(
            QueueStopEvent(stopped_by=stopped_by),
            PublishFrom.APPLICATION_MANAGER
        )
        queue_manager.stop_listen()
