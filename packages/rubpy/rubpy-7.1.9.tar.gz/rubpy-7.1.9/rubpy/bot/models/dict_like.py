
class DictLike:
    """
    A class that allows attribute access via dictionary-like key lookup.

    Provides dictionary-style access (`obj[key]`) to attributes.
    Also supports `get(key, default)` method.

    Methods:
        find_key(key): Recursively searches for a key in nested attributes
                       and returns its value if found, else raises KeyError.

    Example:
        >>> class Example(DictLike):
        ...     def __init__(self):
        ...         self.a = 10
        ...         self.b = DictLike()
        ...         self.b.c = 20
        ...         self.b.d = DictLike()
        ...         self.b.d.e = 30
        ...
        >>> ex = Example()
        >>> ex['a']
        10
        >>> ex.get('a')
        10
        >>> ex.find_key('e')
        30
        >>> ex.find_key('x')
        Traceback (most recent call last):
            ...
        KeyError: 'x'
    """

    key: dict = {'key': {'key': {'new_key': 'hi!'}}}

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def find_key(self, key):
        """
        Recursively searches for the given key in self and nested DictLike attributes.

        Args:
            key (str): The key to search for.

        Returns:
            Any: The value corresponding to the key if found.

        Raises:
            KeyError: If the key is not found in self or nested attributes.
        """
        # Check current level
        if hasattr(self, key):
            return getattr(self, key)

        # Recursively check nested DictLike attributes
        for attr_name in dir(self):
            # Skip special/private attributes
            if attr_name.startswith('_'):
                continue

            attr_value = getattr(self, attr_name, None)
            if isinstance(attr_value, DictLike):
                try:
                    return attr_value.find_key(key)
                except KeyError:
                    pass  # Continue searching

        # Not found
        raise KeyError(key)