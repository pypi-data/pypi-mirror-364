class _Bool:
    __slots__ = ["_value"]

    def __init__(self, value: str):
        self._value = value

    def __bool__(self):
        try:
            return _VALUES[self._value.lower()]
        except KeyError:
            raise ValueError


_VALUES = {
    "1": True,
    "0": False,
    "true": True,
    "false": False,
    "yes": True,
    "no": False,
    "y": True,
    "n": False,
    "on": True,
    "off": False,
}
