from typing import Optional

from .._mock import OpenAIMock
from .._stores.state_store import Resource, StateStore


def add_resource_to_state_store(
    resource: Resource,
    *,
    mock: Optional[OpenAIMock] = None,
    state_store: Optional[StateStore] = None,
):
    """Add a resource to the state store being used for a test. If an object with the same resource
    ID already exists in the state store then it will be overwritten.

    Args:
        resource (Resource): An OpenAI resource
        mock (Optional[OpenAIMock], optional): Mock associated with test. Defaults to None.
        state_store (Optional[StateStore], optional): State store associated with test. Defaults to None.

    Raises:
        ValueError: If neither mock or state store are provided
        ValueError: If both mock and state store are provided
    """
    if not mock and not state_store:
        raise ValueError(
            "Either a mock instance or a state store instance must be provided"
        )

    if mock and state_store:
        raise ValueError(
            "Only one of mock instance or state store instance should be provided not both"
        )

    if mock:
        mock._state._blind_put(resource)

    if state_store:
        state_store._blind_put(resource)
