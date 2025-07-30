# Customizing Converters

When working with {program}`attrs` or dataclasses,
you can choose between two converters:
the built-in {class}`~typed_settings.converters.TSConverter` and
a {class}`cattrs.Converter`.

The built-in converter allows you to use Typed Settings with fewer (or even no) dependencies but it cannot be customized easily.

However, customization is one of {program}`cattrs`' many strengths.
This section provides only a few recipes,
so you may want to read cattrs' full {external+cattrs:doc}`customizing` docs.


## Enums

Typed Settings structures `enum.Enum` instances by name and `enum.StrEnum` as well as `enum.IntEnum` instances by value.

If you don't like this behavior,
you can reconfigure the converter with the help of {func}`typed_settings.converters.to_enum_by_name()` and {func}`typed_settings.converters.to_enum_by_value()`:

```{code-block} python
:caption: example.py
:emphasize-lines: 18,23

import enum
import functools

import typed_settings as ts


class LeEnum(enum.Enum):
    spam = "Le spam"
    eggs = "Le eggs"


@ts.settings
class Settings:
    option: LeEnum


converter = ts.converters.get_default_cattrs_converter()
converter.register_structure_hook(LeEnum, ts.converters.to_enum_by_value)

settings = ts.load_settings(
    Settings,
    ts.default_loaders("myapp"),
    converter=converter
)
print(settings)
```
```{code-block} console
$ MYAPP_OPTION="Le spam" python example.py
Settings(option=<LeEnum.spam: 'Le spam'>)
```

```{admonition} Why different behaviors?
:class: hint

- {program}`Sqlalchemy` (de)structures enums by name when used as column type.
- {program}`Pydantic` and {program}`Cattrs` (de)structure enums by value --
  probably because it is more human readable?
- The first versions of Typed Settings only supported {class}`enum.Enum`.
- It used "by name" because I deemed it safer / less error prone,
  especially when used as command line options (e.g., via {class}`click.Choice`).
- Support for {class}`enum.StrEnum` and {class}`enum.IntEnum` was added in 25.0.
- I decided to follow the example of {program}`Cattrs`/{program}`Pydantic` and
  structure them by value.
  This also makes sense because they inherit `str`/`int` and
  their value is what you get when you call {class}`str`/{class}`int` on them.
- I didn't change the behavior for {class}`enum.Enum` for backwards compatibility.
```
