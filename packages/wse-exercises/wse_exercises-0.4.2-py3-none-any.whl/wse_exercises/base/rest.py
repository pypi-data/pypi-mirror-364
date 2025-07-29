"""Defines pydantic v1 models for REST API."""

import uuid
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import Field

from wse_exercises import AnswerT, ConfigT, ExerciseT, TaskT

from .model import BaseShema


class TaskRequest(BaseShema, Generic[ExerciseT, ConfigT]):
    """Model for request the task.

    :param Exercise name: Exercise name.
    :param ExerciseConfig config: Exercise configuration.
    """

    name: ExerciseT
    config: ConfigT
    is_rewardable: bool = False


class TaskResponse(BaseShema, Generic[TaskT]):
    """Response model with crated task.

    :param uuid.UUID uid: The unique identifier of task.
    :param TaskT task: Created task.
    """

    uid: uuid.UUID
    task: TaskT


class CheckRequest(BaseShema, Generic[AnswerT]):
    """Model for request the answer check.

    :param uuid.UUID uid: The unique identifier of task.
    :param AnswerT answer: Answer to handle.
    :param bool is_rewardable: Is there a reward for the correct answer?
    """

    uid: uuid.UUID
    answer: AnswerT
    is_rewardable: bool = False


class CheckResponse(BaseShema):
    """Response model with user answer check result.

    :param bool is_correct: The user answer check result.
    """

    is_correct: bool
    checked_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


TaskRequestT_contra = TypeVar(
    'TaskRequestT_contra',
    bound=TaskRequest[Any, Any],
    contravariant=True,
)

CheckRequest_contra = TypeVar(
    'CheckRequest_contra',
    bound=CheckRequest[Any],
    contravariant=True,
)
