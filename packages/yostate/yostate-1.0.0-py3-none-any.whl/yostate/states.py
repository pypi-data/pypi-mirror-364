from functools import cached_property
from typing import Any

from pydantic import BaseModel, ConfigDict

from .locators import FrozenLocator, Locator


class BaseState(BaseModel):
    """Base class for all states of state machine.

    Fill free to inherit custom state class from BaseState with adding new attributes to Pydantic model scheme.
    """

    state_class_locator: str
    """
    Path-like string specifies how to find required State class.
    Will be initialized by router on state instance creation.
    """

    model_config = ConfigDict(
        use_attribute_docstrings=True,
        validate_default=True,
        validate_assignment=True,
        extra='ignore',
        frozen=True,
        ignored_types=(cached_property,),
    )

    def enter_state(self) -> Locator | None:
        """Run any custom logic on state enter.

        Can return state object to force state machine switching to another state.
        """
        pass

    async def aenter_state(self) -> Locator | None:
        """Run any custom logic on state enter.

        Can return state object to force state machine switching to another state.
        """
        pass

    def exit_state(self, state_class_transition: bool) -> None:
        """Run any custom logic on state exit.

        State machine switching to another state is not available from this method.
        """
        pass

    async def aexit_state(self, state_class_transition: bool) -> None:
        """Run any custom logic on state exit.

        State machine switching to another state is not available from this method.
        """
        pass

    def process(self, event: Any) -> Locator | None:
        """Run any custom logic to process event.

        Can return state object to force state machine switching to another state.
        """
        pass

    async def aprocess(self, event: Any) -> Locator | None:
        """Run any custom logic to process event.

        Can return state object to force state machine switching to another state.
        """
        pass

    @cached_property
    def locator(self) -> Locator:
        return FrozenLocator.model_validate(
            {
                "state_class_locator": self.state_class_locator,
                "params": self.model_dump(
                    exclude={'state_class_locator'},
                    by_alias=True,
                    exclude_defaults=True,  # Make locators shorter
                ),
            },
        )
