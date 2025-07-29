# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class DndTreeEditor(Component):
    """A DndTreeEditor component.


Keyword arguments:

- id (string; optional)

- collapsible (boolean | number | string | dict | list; default True)

- indentationWidth (number; default 50)

- indicator (boolean | number | string | dict | list; default False)

- items (list of dicts; optional)

    `items` is a list of dicts with keys:

    - id (string; required)

    - parent_id (string; required)

    - label (string; optional)

- onItemsChange (optional)

- onRemove (optional)

- onSelect (optional)

- removable (boolean | number | string | dict | list; default False)

- selectedId (string; optional)

- setProps (optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_sortable_tree'
    _type = 'DndTreeEditor'
    Items = TypedDict(
        "Items",
            {
            "id": str,
            "parent_id": typing.Union[str],
            "label": NotRequired[typing.Union[str]]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        items: typing.Optional[typing.Sequence["Items"]] = None,
        selectedId: typing.Optional[typing.Union[str]] = None,
        collapsible: typing.Optional[typing.Any] = None,
        removable: typing.Optional[typing.Any] = None,
        indicator: typing.Optional[typing.Any] = None,
        indentationWidth: typing.Optional[typing.Union[NumberType]] = None,
        onItemsChange: typing.Optional[typing.Union[typing.Any]] = None,
        onSelect: typing.Optional[typing.Union[typing.Any]] = None,
        onRemove: typing.Optional[typing.Union[typing.Any]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'collapsible', 'indentationWidth', 'indicator', 'items', 'onItemsChange', 'onRemove', 'onSelect', 'removable', 'selectedId', 'setProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'collapsible', 'indentationWidth', 'indicator', 'items', 'onItemsChange', 'onRemove', 'onSelect', 'removable', 'selectedId', 'setProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DndTreeEditor, self).__init__(**args)

setattr(DndTreeEditor, "__init__", _explicitize_args(DndTreeEditor.__init__))
