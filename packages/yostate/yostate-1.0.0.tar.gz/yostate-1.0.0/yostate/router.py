from typing import Type, Callable, Sequence

from pydantic import BaseModel, ConfigDict, ValidationError, validate_call

from .exceptions import LocatorParamsError, NotFoundStateClassLocatorError
from .locators import Locator
from .state_class_locator_validators import StateClassLocatorValidator, validate_state_class_locator
from .states import BaseState


StateDecoratorType = Callable[[Type[BaseState]], Type[BaseState]]


class Route(BaseModel):
    state_class_locator: str
    state_class: Type[BaseState]
    title: str = ''

    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        frozen=True,
    )


class Router(dict[str, Route]):
    """Index of registered state classes."""

    decorators: tuple[StateDecoratorType, ...]
    state_class_locator_validators: tuple[StateClassLocatorValidator, ...]

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        decorators: Sequence[StateDecoratorType] | None = None,
        state_class_locator_validators: Sequence[StateClassLocatorValidator] | None = None,
    ):
        self.decorators = tuple(decorators) if decorators else ()
        if state_class_locator_validators is not None:
            self.state_class_locator_validators = tuple(state_class_locator_validators)
        else:
            self.state_class_locator_validators = (validate_state_class_locator,)

    @validate_call
    def register(
        self,
        state_class_locator: str,
        *,
        title: str = '',
        force: bool = False,
    ) -> Callable[[Type[BaseState]], Type[BaseState]]:
        """Register a State with specified locator."""

        @validate_call
        def register_state_class(state_class: Type[BaseState]) -> Type[BaseState]:
            wrapped_state_class = state_class
            for decorator in reversed(self.decorators):
                wrapped_state_class = decorator(wrapped_state_class)

            cleaned_state_class_locator = self._validate_state_class_locator(state_class_locator)

            route = Route(
                state_class_locator=cleaned_state_class_locator,
                state_class=wrapped_state_class,
                title=title,
            )

            registered_locator = self.get(route.state_class_locator, None)
            if registered_locator and not force:
                raise ValueError('Locator already in use')

            self[route.state_class_locator] = route
            return wrapped_state_class

        return register_state_class

    @validate_call
    def create_state(self, locator: Locator) -> BaseState:
        """Create new serializable State."""
        cleaned_state_class_locator = self._validate_state_class_locator(locator.state_class_locator)

        route = self.get(cleaned_state_class_locator, None)

        if not route:
            raise NotFoundStateClassLocatorError(
                f'Unknown state class locator {locator.state_class_locator!r} with '
                f'normalized value {cleaned_state_class_locator!r}',
            )

        try:
            state_params = locator.params | {'state_class_locator': cleaned_state_class_locator}
            return route.state_class.model_validate(state_params)
        except ValidationError as error:
            raise LocatorParamsError(f'Can`t create state for locator {locator}') from error

    def _validate_state_class_locator(self, value: str) -> str:
        for validate in self.state_class_locator_validators:
            value = validate(value)

        return value
