from enum import Enum
from typing import Union

from sqlalchemy.dialects.postgresql import UUID

from extensions.ext_database import db
from models.account import Account


class CreatedByRole(Enum):
    """
    Created By Role Enum
    """
    ACCOUNT = 'account'
    END_USER = 'end_user'

    @classmethod
    def value_of(cls, value: str) -> 'CreatedByRole':
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f'invalid created by role value {value}')


class WorkflowType(Enum):
    """
    Workflow Type Enum
    """
    WORKFLOW = 'workflow'
    CHAT = 'chat'

    @classmethod
    def value_of(cls, value: str) -> 'WorkflowType':
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f'invalid workflow type value {value}')

    @classmethod
    def from_app_mode(cls, app_mode: Union[str, 'AppMode']) -> 'WorkflowType':
        """
        Get workflow type from app mode.

        :param app_mode: app mode
        :return: workflow type
        """
        from models.model import AppMode
        app_mode = app_mode if isinstance(app_mode, AppMode) else AppMode.value_of(app_mode)
        return cls.WORKFLOW if app_mode == AppMode.WORKFLOW else cls.CHAT


class Workflow(db.Model):
    """
    Workflow, for `Workflow App` and `Chat App workflow mode`.

    Attributes:

    - id (uuid) Workflow ID, pk
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - type (string) Workflow type

        `workflow` for `Workflow App`

        `chat` for `Chat App workflow mode`

    - version (string) Version

        `draft` for draft version (only one for each app), other for version number (redundant)

    - graph (text) Workflow canvas configuration (JSON)

        The entire canvas configuration JSON, including Node, Edge, and other configurations

        - nodes (array[object]) Node list, see Node Schema

        - edges (array[object]) Edge list, see Edge Schema

    - created_by (uuid) Creator ID
    - created_at (timestamp) Creation time
    - updated_by (uuid) `optional` Last updater ID
    - updated_at (timestamp) `optional` Last update time
    """

    __tablename__ = 'workflows'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='workflow_pkey'),
        db.Index('workflow_version_idx', 'tenant_id', 'app_id', 'version'),
    )

    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(UUID, nullable=False)
    app_id = db.Column(UUID, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    graph = db.Column(db.Text)
    created_by = db.Column(UUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_by = db.Column(UUID)
    updated_at = db.Column(db.DateTime)

    @property
    def created_by_account(self):
        return Account.query.get(self.created_by)

    @property
    def updated_by_account(self):
        return Account.query.get(self.updated_by)


class WorkflowRunTriggeredFrom(Enum):
    """
    Workflow Run Triggered From Enum
    """
    DEBUGGING = 'debugging'
    APP_RUN = 'app-run'

    @classmethod
    def value_of(cls, value: str) -> 'WorkflowRunTriggeredFrom':
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f'invalid workflow run triggered from value {value}')


class WorkflowRunStatus(Enum):
    """
    Workflow Run Status Enum
    """
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    STOPPED = 'stopped'

    @classmethod
    def value_of(cls, value: str) -> 'WorkflowRunStatus':
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f'invalid workflow run status value {value}')


class WorkflowRun(db.Model):
    """
    Workflow Run

    Attributes:

    - id (uuid) Run ID
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - sequence_number (int) Auto-increment sequence number, incremented within the App, starting from 1
    - workflow_id (uuid) Workflow ID
    - type (string) Workflow type
    - triggered_from (string) Trigger source

        `debugging` for canvas debugging

        `app-run` for (published) app execution

    - version (string) Version
    - graph (text) Workflow canvas configuration (JSON)
    - inputs (text) Input parameters
    - status (string) Execution status, `running` / `succeeded` / `failed` / `stopped`
    - outputs (text) `optional` Output content
    - error (string) `optional` Error reason
    - elapsed_time (float) `optional` Time consumption (s)
    - total_tokens (int) `optional` Total tokens used
    - total_price (decimal) `optional` Total cost
    - currency (string) `optional` Currency, such as USD / RMB
    - total_steps (int) Total steps (redundant), default 0
    - created_by_role (string) Creator role

        - `account` Console account

        - `end_user` End user

    - created_by (uuid) Runner ID
    - created_at (timestamp) Run time
    - finished_at (timestamp) End time
    """

    __tablename__ = 'workflow_runs'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='workflow_run_pkey'),
        db.Index('workflow_run_triggerd_from_idx', 'tenant_id', 'app_id', 'triggered_from'),
    )

    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(UUID, nullable=False)
    app_id = db.Column(UUID, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    workflow_id = db.Column(UUID, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    triggered_from = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    graph = db.Column(db.Text)
    inputs = db.Column(db.Text)
    status = db.Column(db.String(255), nullable=False)
    outputs = db.Column(db.Text)
    error = db.Column(db.Text)
    elapsed_time = db.Column(db.Float, nullable=False, server_default=db.text('0'))
    total_tokens = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    total_price = db.Column(db.Numeric(10, 7))
    currency = db.Column(db.String(255))
    total_steps = db.Column(db.Integer, server_default=db.text('0'))
    created_by_role = db.Column(db.String(255), nullable=False)
    created_by = db.Column(UUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    finished_at = db.Column(db.DateTime)

    @property
    def created_by_account(self):
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return Account.query.get(self.created_by) \
            if created_by_role == CreatedByRole.ACCOUNT else None

    @property
    def created_by_end_user(self):
        from models.model import EndUser
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return EndUser.query.get(self.created_by) \
            if created_by_role == CreatedByRole.END_USER else None


class WorkflowNodeExecutionTriggeredFrom(Enum):
    """
    Workflow Node Execution Triggered From Enum
    """
    SINGLE_STEP = 'single-step'
    WORKFLOW_RUN = 'workflow-run'

    @classmethod
    def value_of(cls, value: str) -> 'WorkflowNodeExecutionTriggeredFrom':
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f'invalid workflow node execution triggered from value {value}')


class WorkflowNodeExecution(db.Model):
    """
    Workflow Node Execution

    - id (uuid) Execution ID
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - workflow_id (uuid) Workflow ID
    - triggered_from (string) Trigger source

        `single-step` for single-step debugging

        `workflow-run` for workflow execution (debugging / user execution)

    - workflow_run_id (uuid) `optional` Workflow run ID

        Null for single-step debugging.

    - index (int) Execution sequence number, used for displaying Tracing Node order
    - predecessor_node_id (string) `optional` Predecessor node ID, used for displaying execution path
    - node_id (string) Node ID
    - node_type (string) Node type, such as `start`
    - title (string) Node title
    - inputs (json) All predecessor node variable content used in the node
    - process_data (json) Node process data
    - outputs (json) `optional` Node output variables
    - status (string) Execution status, `running` / `succeeded` / `failed`
    - error (string) `optional` Error reason
    - elapsed_time (float) `optional` Time consumption (s)
    - execution_metadata (text) Metadata

        - total_tokens (int) `optional` Total tokens used

        - total_price (decimal) `optional` Total cost

        - currency (string) `optional` Currency, such as USD / RMB

    - created_at (timestamp) Run time
    - created_by_role (string) Creator role

        - `account` Console account

        - `end_user` End user

    - created_by (uuid) Runner ID
    - finished_at (timestamp) End time
    """

    __tablename__ = 'workflow_node_executions'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='workflow_node_execution_pkey'),
        db.Index('workflow_node_execution_workflow_run_idx', 'tenant_id', 'app_id', 'workflow_id',
                 'triggered_from', 'workflow_run_id'),
        db.Index('workflow_node_execution_node_run_idx', 'tenant_id', 'app_id', 'workflow_id',
                 'triggered_from', 'node_id'),
    )

    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(UUID, nullable=False)
    app_id = db.Column(UUID, nullable=False)
    workflow_id = db.Column(UUID, nullable=False)
    triggered_from = db.Column(db.String(255), nullable=False)
    workflow_run_id = db.Column(UUID)
    index = db.Column(db.Integer, nullable=False)
    predecessor_node_id = db.Column(db.String(255))
    node_id = db.Column(db.String(255), nullable=False)
    node_type = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    inputs = db.Column(db.Text, nullable=False)
    process_data = db.Column(db.Text, nullable=False)
    outputs = db.Column(db.Text)
    status = db.Column(db.String(255), nullable=False)
    error = db.Column(db.Text)
    elapsed_time = db.Column(db.Float, nullable=False, server_default=db.text('0'))
    execution_metadata = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    created_by_role = db.Column(db.String(255), nullable=False)
    created_by = db.Column(UUID, nullable=False)
    finished_at = db.Column(db.DateTime)

    @property
    def created_by_account(self):
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return Account.query.get(self.created_by) \
            if created_by_role == CreatedByRole.ACCOUNT else None

    @property
    def created_by_end_user(self):
        from models.model import EndUser
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return EndUser.query.get(self.created_by) \
            if created_by_role == CreatedByRole.END_USER else None


class WorkflowAppLog(db.Model):
    """
    Workflow App execution log, excluding workflow debugging records.

    Attributes:

    - id (uuid) run ID
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - workflow_id (uuid) Associated Workflow ID
    - workflow_run_id (uuid) Associated Workflow Run ID
    - created_from (string) Creation source

        `service-api` App Execution OpenAPI

        `web-app` WebApp

        `installed-app` Installed App

    - created_by_role (string) Creator role

        - `account` Console account

        - `end_user` End user

    - created_by (uuid) Creator ID, depends on the user table according to created_by_role
    - created_at (timestamp) Creation time
    """

    __tablename__ = 'workflow_app_logs'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='workflow_app_log_pkey'),
        db.Index('workflow_app_log_app_idx', 'tenant_id', 'app_id'),
    )

    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(UUID, nullable=False)
    app_id = db.Column(UUID, nullable=False)
    workflow_id = db.Column(UUID, nullable=False)
    workflow_run_id = db.Column(UUID, nullable=False)
    created_from = db.Column(db.String(255), nullable=False)
    created_by_role = db.Column(db.String(255), nullable=False)
    created_by = db.Column(UUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def workflow_run(self):
        return WorkflowRun.query.get(self.workflow_run_id)

    @property
    def created_by_account(self):
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return Account.query.get(self.created_by) \
            if created_by_role == CreatedByRole.ACCOUNT else None

    @property
    def created_by_end_user(self):
        from models.model import EndUser
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return EndUser.query.get(self.created_by) \
            if created_by_role == CreatedByRole.END_USER else None
