from typing import Callable, Type, Any, Awaitable

from collections import defaultdict
import asyncio


class EventBus:
    """
    Asynchronous event bus.
    """

    def __init__(self) -> None:
        """
        Initialize an empty EventBus instance.

        Attributes:
                _subscribers (dict[Type, list[Callable[[Any], Awaitable[None]]]]):
                        Internal mapping between an event type and a list of
                        asynchronous handler functions subscribed to that type.
        """
        self._subscribers: dict[Type, list[Callable[[Any], Awaitable[None]]]] = (
            defaultdict(list)
        )

    def subscribe(
        self, event_type: Type, handler: Callable[[Any], Awaitable[None]]
    ) -> None:
        """
        Subscribe an asynchronous handler to a specific event type.

        Args:
                event_type (Type):
                        The class/type of the event to subscribe to. Handlers
                        will be triggered only when an instance of this exact
                        type is published.

                handler (Callable[[Any], Awaitable[None]]):
                        An asynchronous callable (coroutine function) that
                        receives the event instance as its only argument.
        """

        self._subscribers[event_type].append(handler)

    async def publish(self, event: Any) -> None:
        """
        Publish an event to all subscribed handlers asynchronously.

        All handlers registered for the exact type of the given event
        will be executed concurrently using ``asyncio.gather``.

        Args:
                event (Any):
                        The event instance to publish. Its runtime type
                        determines which handlers are invoked.
        """

        handlers = self._subscribers.get(type(event), [])

        if not handlers:
            return

        await asyncio.gather(*(handler(event) for handler in handlers))
