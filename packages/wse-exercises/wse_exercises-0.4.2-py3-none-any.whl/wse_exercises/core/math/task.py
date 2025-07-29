"""Defines the math task Data Transfer Objects."""

from wse_exercises.base.task import Task

from .base.components import (
    SimpleCalcAnswer,
    SimpleCalcConditions,
    SimpleCalcConfig,
    SimpleCalcQuestion,
)
from .enums import MathEnum


class SimpleCalcTask(
    Task[
        SimpleCalcConfig,
        SimpleCalcConditions,
        SimpleCalcQuestion,
        SimpleCalcAnswer,
        MathEnum,
    ]
):
    """Base simple math task with text question/answer.

    :param config: Contains the min and max values of the operands.
    :param conditions: Contain the first and second operand values.
    :param question: The text representation of question.
    :param answer: The text representation of answer.
    :param exercise_name: Exercise name.
    :param created: The data and time of task creation.
    """

    config: SimpleCalcConfig
    conditions: SimpleCalcConditions
    question: SimpleCalcQuestion
    answer: SimpleCalcAnswer
    exercise_name: MathEnum
