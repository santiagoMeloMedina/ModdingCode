import enum
from typing import List, Optional

import pydantic

from modding.common import model


class ProblemStatus(enum.Enum):
    CREATED = "CREATED"
    DETAILED = "DETAILED"
    COMPLETED = "COMPLETED"


class ProblemDescription(model.Model):
    description: Optional[str]
    sample_input: Optional[str]
    sample_output: Optional[str]


class ProblemInputFile(model.Model):
    id: str
    input_name: str
    output_name: str
    input_id: str
    output_id: str
    input_data: Optional[str]
    output_data: Optional[str]


class Problem(model.Model):
    name: str
    minicourse_id: str
    description: Optional[ProblemDescription]
    test_case: Optional[List[ProblemInputFile]]
    difficulty: int
    status: ProblemStatus

    class Config:
        use_enum_values = True


class ProblemVeredict(enum.Enum):
    SENT = "SENT"
    FAILED = "FAILED"
    SOLVED = "SOLVED"


class InputVeredict(pydantic.BaseModel):
    id: str
    veredict: ProblemVeredict

    class Config:
        use_enum_values = True


class ProblemEvaluation(model.ModelShown):
    problem_id: str
    veredict: ProblemVeredict
    veredict_reason: Optional[List[str]]
    inputs_veredict: Optional[List[InputVeredict]]

    class Config:
        use_enum_values = True
