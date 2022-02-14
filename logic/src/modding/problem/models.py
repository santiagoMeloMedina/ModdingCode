import enum
from typing import List, Optional

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


class ProblemEvaluation(model.ModelShown):
    problem_id: str
    veredict: ProblemVeredict

    class Config:
        use_enum_values = True
