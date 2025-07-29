"""WSE mathematical exercises."""

__all__ = [
    'AddingExercise',
    'DivisionExercise',
    'ExactOperandGenerator',
    'MultiplicationExercise',
    'RandomOperandGenerator',
    'SimpleCalcAnswer',
    'SimpleCalcConditions',
    'SimpleCalcConfig',
    'SimpleCalcQuestion',
    'SubtractionExercise',
    'SimpleCalcTask',
]

from .base.components import (
    SimpleCalcAnswer,
    SimpleCalcConditions,
    SimpleCalcConfig,
    SimpleCalcQuestion,
)
from .exercises import (
    AddingExercise,
    DivisionExercise,
    MultiplicationExercise,
    SubtractionExercise,
)
from .services.operand_generator import (
    ExactOperandGenerator,
    RandomOperandGenerator,
)
from .task import (
    SimpleCalcTask,
)
