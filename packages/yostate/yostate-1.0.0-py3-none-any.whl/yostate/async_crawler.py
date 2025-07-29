import logging
from itertools import count
from typing import Any, cast, final

from pydantic import ConfigDict, validate_call
from pydantic.dataclasses import dataclass

from .exceptions import (
    DetachedCrawlerError,
    LocatorError,
    TooLongTransitionError,
)
from .router import Locator, Router
from .states import BaseState

logger = logging.getLogger('yostate')


@final
@dataclass(config=ConfigDict(arbitrary_types_allowed=True, use_attribute_docstrings=True))
class AsyncCrawler:
    router: Router
    current_state: BaseState | None = None
    max_transition_length: int = 20
    """Настраивает защиту от зацикливания. Он ограничивает максимальную длину
    непрерывной цепочки переходов между состояниями."""

    @validate_call
    def restore(self, locator: Locator, ignore_errors: bool = False) -> None:
        """Восстанавливает положение краулера в прежнем состоянии.

        Используйте метод `restore`, чтобы восстановить положение краулера в том состоянии, где он ранее прервал
        свою работу.
        Вызов метода `restore` отличается от `switch_to` тем, что не приводит к запуску кода в методе
        `BaseState.enter_state` и не запускает процесс переходов по состояниям.
        """
        try:
            self.current_state = self.router.create_state(locator)
        except LocatorError:
            if not ignore_errors:
                raise
            logger.warning('Crawler restore failed for locator %s', locator)

    def detach(self) -> None:
        self.current_state = None

    async def process(self, event: Any) -> None:
        """Обрабатывает поступившее событие."""
        if self.attached:
            current_state = cast(BaseState, self.current_state)
        else:
            raise DetachedCrawlerError('Crawler is not attached yet')

        next_locator = await current_state.aprocess(event=event)

        if next_locator:
            await self.switch_to(next_locator)

    @validate_call
    async def switch_to(self, locator: Locator) -> None:  # noqa CCR001
        """Переводит краулер в новое состояние и следует далее по цепочке переходов до упора.

        В краулер встроена защиты от зацикливания. Она ограничивает максимальную длину цепочки переходов.
        """
        next_state = self.router.create_state(locator)

        counter = count(1)

        prev_state = self.current_state

        for transition_length in counter:
            if transition_length > self.max_transition_length:
                raise TooLongTransitionError(
                    f'Transition length limit of {self.max_transition_length} is exceeded.',
                )

            logger.debug(
                'State %s → %s.',
                prev_state and prev_state.state_class_locator,
                next_state.state_class_locator,
            )
            logger.debug('    Old: %s', prev_state)
            logger.debug('    New: %s', next_state)

            state_class_transition = type(prev_state) is type(next_state)

            if prev_state:
                await prev_state.aexit_state(state_class_transition=state_class_transition)

            next_next_locator = await next_state.aenter_state()
            if not next_next_locator:
                break

            next_next_state = self.router.create_state(next_next_locator)
            prev_state, next_state = next_state, next_next_state

        self.current_state = next_state

    @property
    def attached(self) -> bool:
        return bool(self.current_state)
