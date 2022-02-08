from typing import Any, Callable, Dict, List, Tuple
import uuid


def generate_id(prefix: str, length: int) -> str:
    random_code = str(uuid.uuid4()).replace("-", "")
    return f"{prefix}-{random_code[:length]}"


def retrier_caller(
    func: Callable,
    params: Tuple[List[str], Dict[str, Any]],
    tries: int,
    logging_method: Callable = None,
    failed_message: str = None,
) -> Any:
    try_number = 0
    while try_number < tries:
        try:
            args, kwargs = params
            return func(*args, **kwargs)
        except Exception as e:
            try_number += 1
            if logging_method:
                logging_method(
                    f"{'%s, ' % (failed_message) if failed_message else ''}try #{try_number}, {e}"
                )

    if logging_method:
        logging_method("Failed all tries")


def retrier_with_generator(prefix: str, length: int, **kwargs: Any) -> Any:
    """
    func: Callable,
    params: (*args, **kwargs),
    tries: int,
    logging_method: Callable = None,
    failed_message: str = None"""

    func = kwargs.get("func")

    def __generate_id_and_call(*func_args: Any, **func_kwargs: Any) -> Any:
        func_kwargs.update({**func_kwargs, "id": generate_id(prefix, length)})
        return func(*func_args, **func_kwargs)

    kwargs.update({"func": __generate_id_and_call})

    return retrier_caller(**kwargs)
