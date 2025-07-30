[![Coverage Status](https://coveralls.io/repos/github/datek/enfig/badge.svg?branch=master)](https://coveralls.io/github/datek/enfig?branch=master)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<a href="https://github.com/psf/black/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>

# Enfig - Environment Config

Lean, zero dependency environment parsing library based on annotations,
inspired by [pydantic](https://github.com/pydantic/pydantic).

Environmental variables are being parsed and casted automatically to the corresponding type
when class variables are being accessed.

## Examples:

```python

import os
import enfig

# Just for demonstration, of course env vars should already be set outside the application.
os.environ["COLOR"] = "RED"
os.environ["TEMPERATURE"] = "50"
os.environ["DISABLE_AUTOTUNE"] = "y"


class Config(enfig.BaseConfig):
    COLOR: str
    TEMPERATURE: int
    DISABLE_AUTOTUNE: bool


assert Config.COLOR == "RED"
assert Config.TEMPERATURE == 50
assert Config.DISABLE_AUTOTUNE is True
```

The `Config` class casts the values automatically.
Moreover, you can test if all mandatory variables have been set and have the correct type.

```python
import os
import enfig

os.environ["COLOR"] = "RED"
os.environ["DISABLE_AUTOTUNE"] = "I can't sing but I pretend to be a singer"
os.environ["WEIGHT"] = "haha invalid"


class Config(enfig.BaseConfig):
    COLOR: str
    TEMPERATURE: int
    WEIGHT: float
    AMOUNT: int = None
    DISABLE_AUTOTUNE: bool = None


try:
    Config.validate()
except enfig.ValidationError as error:
    for attribute_error in error.errors:
        print(attribute_error)

```
Output:
```
DISABLE_AUTOTUNE: Invalid value, required type: `bool`
TEMPERATURE: Not set, required type: `int`
WEIGHT: Invalid value, required type: `float`
```
