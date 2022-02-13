from typing import Callable


def decorator_builder(middleware: Callable, *args, **kwargs):
    ### Very imporant method, in charge on handling decorators
    ### for handlers

    extra_kwargs = middleware(*args, **kwargs)

    def decorator(function: Callable):
        def wrapper(*args, **kwargs):
            return function(*args, **{**kwargs, **extra_kwargs})

        return wrapper

    return decorator
