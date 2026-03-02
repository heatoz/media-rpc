from mpcrpc.infra import EventBus
from dataclasses import dataclass
from typing import Any
import pytest

@dataclass
class DataModel:
	"""A simple data model to attach to events."""
	id: int
	name: str
	active: bool

class EventTest:
	"""An event class carrying a DataModel instance."""

	def __init__(self, data: DataModel) -> None:
		self.data = data

class AnotherEvent:
	"""A different event type to test event-type isolation."""

@pytest.mark.asyncio(loop_scope="class")
class TestEventBus:
	"""
	Test suite for the asynchronous EventBus class.
	Verifies subscription, publishing, handler invocation, and event content integrity.
	"""

	async def test_subscribe_and_publish_invokes_handler(self) -> None:
		"""
		Ensure that a handler subscribed to a specific event type
		is invoked when that event is published.
		"""
		bus = EventBus()
		called: bool = False

		async def handler(event: EventTest) -> None:
			nonlocal called
			called = True

		bus.subscribe(EventTest, handler)
		await bus.publish(EventTest(DataModel(1, "Alice", True)))
		assert called, "Subscribed handler was not called upon event publish"

	async def test_handler_receives_event_content(self) -> None:
		"""
		Ensure that the event instance and its data content are
		correctly received by the handler.
		"""
		bus = EventBus()
		received_data: Any = None

		async def handler(event: EventTest) -> None:
			nonlocal received_data
			received_data = event.data

		model_instance = DataModel(42, "Bob", False)
		bus.subscribe(EventTest, handler)
		await bus.publish(EventTest(model_instance))

		assert received_data is model_instance, "Handler did not receive correct DataModel instance"
		assert received_data.id == 42, "DataModel.id mismatch"
		assert received_data.name == "Bob", "DataModel.name mismatch"
		assert received_data.active is False, "DataModel.active mismatch"

	async def test_multiple_handlers_receive_correct_data(self) -> None:
		"""
		Verify that multiple handlers subscribed to the same event type
		all receive the same event instance with correct data.
		"""
		bus = EventBus()
		received: list[DataModel] = []

		async def handler1(event: EventTest) -> None:
			received.append(event.data)

		async def handler2(event: EventTest) -> None:
			received.append(event.data)

		model_instance = DataModel(7, "Charlie", True)
		bus.subscribe(EventTest, handler1)
		bus.subscribe(EventTest, handler2)
		await bus.publish(EventTest(model_instance))

		assert all(r is model_instance for r in received), "Handlers did not receive correct event instance"
		assert len(received) == 2, "Not all handlers received the event"

	async def test_no_handler_registered_does_not_fail(self) -> None:
		"""
		Verify that publishing an event with no subscribed handlers
		completes successfully without raising an exception.
		"""
		bus = EventBus()
		try:
			await bus.publish(AnotherEvent())
		except Exception as e:
			pytest.fail(f"Publishing event with no handlers raised an exception: {e}")

	async def test_handlers_only_triggered_for_exact_type(self) -> None:
		"""
		Ensure that handlers are only invoked for the exact event type
		they are subscribed to, not subclasses or unrelated event types.
		"""
		bus = EventBus()
		called: bool = False

		async def handler(event: EventTest) -> None:
			nonlocal called
			called = True

		bus.subscribe(EventTest, handler)
		await bus.publish(AnotherEvent())
		assert not called, "Handler was incorrectly triggered by a different event type"