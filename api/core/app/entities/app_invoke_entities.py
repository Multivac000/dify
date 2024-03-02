from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from core.app.app_config.entities import EasyUIBasedAppConfig, WorkflowUIBasedAppConfig, AppConfig
from core.entities.provider_configuration import ProviderModelBundle
from core.file.file_obj import FileObj
from core.model_runtime.entities.model_entities import AIModelEntity


class InvokeFrom(Enum):
    """
    Invoke From.
    """
    SERVICE_API = 'service-api'
    WEB_APP = 'web-app'
    EXPLORE = 'explore'
    DEBUGGER = 'debugger'

    @classmethod
    def value_of(cls, value: str) -> 'InvokeFrom':
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f'invalid invoke from value {value}')

    def to_source(self) -> str:
        """
        Get source of invoke from.

        :return: source
        """
        if self == InvokeFrom.WEB_APP:
            return 'web_app'
        elif self == InvokeFrom.DEBUGGER:
            return 'dev'
        elif self == InvokeFrom.EXPLORE:
            return 'explore_app'
        elif self == InvokeFrom.SERVICE_API:
            return 'api'

        return 'dev'


class ModelConfigWithCredentialsEntity(BaseModel):
    """
    Model Config With Credentials Entity.
    """
    provider: str
    model: str
    model_schema: AIModelEntity
    mode: str
    provider_model_bundle: ProviderModelBundle
    credentials: dict[str, Any] = {}
    parameters: dict[str, Any] = {}
    stop: list[str] = []


class AppGenerateEntity(BaseModel):
    """
    App Generate Entity.
    """
    task_id: str

    # app config
    app_config: AppConfig

    inputs: dict[str, str]
    files: list[FileObj] = []
    user_id: str

    # extras
    stream: bool
    invoke_from: InvokeFrom

    # extra parameters, like: auto_generate_conversation_name
    extras: dict[str, Any] = {}


class EasyUIBasedAppGenerateEntity(AppGenerateEntity):
    """
    Chat Application Generate Entity.
    """
    # app config
    app_config: EasyUIBasedAppConfig
    model_config: ModelConfigWithCredentialsEntity

    query: Optional[str] = None


class ChatAppGenerateEntity(EasyUIBasedAppGenerateEntity):
    """
    Chat Application Generate Entity.
    """
    conversation_id: Optional[str] = None


class CompletionAppGenerateEntity(EasyUIBasedAppGenerateEntity):
    """
    Completion Application Generate Entity.
    """
    pass


class AgentChatAppGenerateEntity(EasyUIBasedAppGenerateEntity):
    """
    Agent Chat Application Generate Entity.
    """
    conversation_id: Optional[str] = None


class AdvancedChatAppGenerateEntity(AppGenerateEntity):
    """
    Advanced Chat Application Generate Entity.
    """
    # app config
    app_config: WorkflowUIBasedAppConfig

    conversation_id: Optional[str] = None
    query: Optional[str] = None


class WorkflowUIBasedAppGenerateEntity(AppGenerateEntity):
    """
    Workflow UI Based Application Generate Entity.
    """
    # app config
    app_config: WorkflowUIBasedAppConfig
