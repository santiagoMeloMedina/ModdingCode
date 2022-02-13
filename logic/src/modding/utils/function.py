from typing import Callable


def decorator_builder(middleware: Callable, *args, **kwargs):
    extra_kwargs = middleware(*args, **kwargs)

    def decorator(function: Callable):
        def wrapper(*args, **kwargs):
            function(*args, **{**kwargs, **extra_kwargs})

        return wrapper

    return decorator
