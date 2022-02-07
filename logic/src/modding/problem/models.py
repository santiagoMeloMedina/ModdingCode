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


class ProblemTestCase(model.Model):
    input_files: List[str] = list()
    output_files: List[str] = list()


class Problem(model.Model):
    id: str
    name: str
    minicourse_id: str
    description: Optional[ProblemDescription]
    test_case: Optional[ProblemTestCase]
    difficulty: int
    status: ProblemStatus

    class Config:
        use_enum_values = True
