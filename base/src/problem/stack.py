from src.commons import entities
from singleton_injector import injector


@injector
class ProblemStack(entities.Stack):
    def __init__(self):
        super().__init__(id="ProblemStack", name="ProblemStack")
