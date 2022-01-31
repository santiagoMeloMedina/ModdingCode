from src.commons import entities
from singleton_injector import injector


@injector
class MinicourseStack(entities.Stack):
    def __init__(self):
        super().__init__(id="MinicourseStack", name="MinicourseStack")
