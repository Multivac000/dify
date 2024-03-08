from core.workflow.entities.base_node_data_entities import BaseNodeData
from core.workflow.entities.variable_entities import VariableSelector

from pydantic import BaseModel
from typing import Literal, Union

class CodeNodeData(BaseNodeData):
    """
    Code Node Data.
    """
    class Output(BaseModel):
        type: Literal['string', 'number', 'object', 'array[string]', 'array[number]']
        children: Union[None, dict[str, 'Output']]

    variables: list[VariableSelector]
    answer: str
    code_language: str
    code: str
    outputs: dict[str, Output]
