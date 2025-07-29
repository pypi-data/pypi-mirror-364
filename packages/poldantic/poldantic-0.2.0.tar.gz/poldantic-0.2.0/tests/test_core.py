from typing import List, Optional, Union
from pydantic import BaseModel
import polars as pl
from poldantic import to_polars_schema


def test_simple_schema():
    class User(BaseModel):
        id: int
        name: str
        active: bool

    schema = to_polars_schema(User)
    assert schema == {
        "id": pl.Int64(),
        "name": pl.Utf8(),
        "active": pl.Boolean()
    }


def test_nested_schema():
    class Address(BaseModel):
        street: str
        zip: int

    class Customer(BaseModel):
        id: int
        address: Address

    schema = to_polars_schema(Customer)
    assert isinstance(schema["address"], pl.Struct)
    assert dict(schema["address"]) == {
        "street": pl.Utf8(),
        "zip": pl.Int64()
    }


def test_list_field():
    class TagSet(BaseModel):
        tags: list[str]

    schema = to_polars_schema(TagSet)
    assert schema["tags"] == pl.List(pl.Utf8())
