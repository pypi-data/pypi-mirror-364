from typing import Any, get_args, get_origin, Type, Union, List
import polars as pl
from pydantic import BaseModel
import datetime

PYTHON_TO_POLARS = {
    int: pl.Int64(),
    float: pl.Float64(),
    str: pl.Utf8(),
    bool: pl.Boolean(),
    bytes: pl.Binary(),
    datetime.date: pl.Date(),
    datetime.datetime: pl.Datetime(),
}


def _resolve_type(py_type: Any) -> pl.DataType:
    origin = get_origin(py_type)
    args = get_args(py_type)

    if origin is Union:
        if type(None) in args and len(args) == 2:
            sub_type = [t for t in args if t is not type(None)][0]
            return _resolve_type(sub_type)
        return pl.Object()  # fallback for mixed Unions

    if origin in (list, List):
        return pl.List(_resolve_type(args[0]))

    if isinstance(py_type, type) and issubclass(py_type, BaseModel):
        return _model_to_struct(py_type)

    if py_type in PYTHON_TO_POLARS:
        return PYTHON_TO_POLARS[py_type]

    return pl.Object()  # final fallback


def _model_to_struct(model: Type[BaseModel]) -> pl.Struct:
    return pl.Struct([
        pl.Field(name=name, dtype=_resolve_type(field.annotation))
        for name, field in model.model_fields.items()
    ])


def to_polars_schema(model: Type[BaseModel]) -> dict[str, pl.DataType]:
    """
    Convert a Pydantic model into a Polars-compatible schema dictionary.

    Parameters
    ----------
    model : Type[pydantic.BaseModel]
        The Pydantic model class to convert.

    Returns
    -------
    dict[str, polars.DataType]
        A dictionary suitable for use as a Polars schema,
        mapping field names to Polars types.

    Examples
    --------
    >>> class User(BaseModel):
    ...     id: int
    ...     name: str
    ...
    >>> to_polars_schema(User)
    {'id': Int64, 'name': Utf8}
    """
    return {
        name: _resolve_type(field.annotation)
        for name, field in model.model_fields.items()
    }