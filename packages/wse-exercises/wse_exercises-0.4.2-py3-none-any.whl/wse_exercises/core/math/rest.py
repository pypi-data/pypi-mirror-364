"""Defines pydantic v1 models for simple calc math task REST API."""

from pydantic import Field
from typing_extensions import Self

from wse_exercises.base.components import NumberAnswer
from wse_exercises.base.rest import (
    CheckRequest,
    CheckResponse,
    TaskRequest,
    TaskResponse,
)

from . import SimpleCalcConfig
from .enums import MathEnum
from .task import SimpleCalcTask


class SimpleCalcRequest(TaskRequest[MathEnum, SimpleCalcConfig]):
    """Model for request the simple calculation task."""

    name: MathEnum
    config: SimpleCalcConfig


class SimpleCalcResponse(TaskResponse[SimpleCalcTask]):
    """Response model with crated simple calculation task."""

    task: SimpleCalcTask


class SimpleCalcCheck(CheckRequest[NumberAnswer]):
    """Model for request the answer handling of simple calculation."""

    answer: NumberAnswer


class SimpleCalcResult(CheckResponse):
    """Response model with simple calculation answer checking result."""

    expression: str | None = Field(
        default=None,
        description='Mathematical expression of the task with the answer',
    )

    def with_correct_answer(self, task_dto: SimpleCalcTask) -> Self:
        """Add expression of the task with the answer.

        For examole:
            result_dto = result_dto.with_expression(task_dto)
        """
        if self.is_correct:
            return self

        expression = f'{task_dto.question.text} = {task_dto.answer.number}'
        return self.copy(update={'expression': expression})
