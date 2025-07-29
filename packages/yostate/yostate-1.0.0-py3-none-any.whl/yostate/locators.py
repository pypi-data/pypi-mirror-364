from typing import Any

from pydantic import BaseModel, ConfigDict


class Locator(BaseModel):
    state_class_locator: str
    params: dict[str, Any] = {}

    model_config = ConfigDict(
        validate_default=True,  # default values should be validated too
        validate_assignment=True,
        extra='forbid',
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Like common pydantic.BaseModel init method with support of positional argument `state_class_locator`.

        Full compatibility with pydantic.BaseModel.__init__ method is provided.
        """
        if len(args) == 1:
            super().__init__(state_class_locator=args[0], **kwargs)
        else:
            super().__init__(**kwargs)


class FrozenLocator(Locator):
    model_config = ConfigDict(
        frozen=True,
    )
