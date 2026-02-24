from typing import Any

class Cache:
    """
    Basic in-memory cache without expiration policy.

    Created to keep project boundaries well delimited and preserve modularity.
    """

    def put(self, key: str, value: Any) -> None:
        """
        Store a value in the cache under the given key.

        The value is stored as an attribute of the Cache instance.

        Args:
            key (str):
                The key under which the value will be stored.
                Must be a valid Python attribute name.
                
            value (Any):
                The value to be cached.
        """

        return setattr(self, key, value)

    def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache by its key.

        Args:
            key (str):
                The key associated with the cached value.

        Returns:
            Any:
                The cached value associated with the given key.

        Raises:
            AttributeError:
                If the key does not exist in the cache.
        """

        return getattr(self, key)