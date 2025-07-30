import random
from functools import wraps
from typing import Callable


class ChaosInjector:

    @classmethod
    def inject(
        cls,
        obj: object,
        probability: float = 0.5,
        decider: Callable[[str], bool] | None = None,
        method_probs: dict[str, float] | None = None
    ) -> None:
        if not (0 <= probability <= 1):
            raise ValueError(
                f"Probability must be between 0 and 1, got {probability}"
            )

        if method_probs:
            invalid_probs = {
                k: v
                for k, v in method_probs.items()
                if not (0 <= v <= 1)
            }
            if invalid_probs:
                raise ValueError(
                    "Method probabilities must be between 0 and 1, "
                    f"invalid: {invalid_probs}"
                )

        def should_use_real(name: str) -> bool:
            if decider:
                return decider(name)
            if method_probs and name in method_probs:
                return random.random() < method_probs[name]
            return random.random() < probability

        ProxyCls = type(
            f"Proxy_{obj.__class__.__name__}",
            (obj.__class__,),
            {
                "__getattribute__": cls.__handle(
                    getattr(obj, "__getattribute__"), should_use_real,
                )
            }
        )
        obj.__class__ = ProxyCls

    @staticmethod
    def __handle(
        original_getattr: Callable,
        should_use_real: Callable[[str], bool],
    ) -> Callable:
        @wraps(original_getattr)
        def wrapper(_, name: str):
            _attr = original_getattr(name)
            if should_use_real(name):
                return _attr

            if callable(_attr):
                return lambda *args, **kwargs: None
            else:
                return None

        return wrapper
