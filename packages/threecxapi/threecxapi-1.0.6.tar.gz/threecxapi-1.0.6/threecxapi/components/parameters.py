from abc import ABC
from typing import Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from enum import Enum


class QueryParameters(BaseModel, ABC, validate_assignment=True): ...


class ListParameters(QueryParameters):
    """
    top (int): The number of items to retrieve from the top.
    skip (int): The number of items to skip.
    search (str): The search query.
    filter (str): The filter to apply.
    count (bool): Indicates if a count should be returned or not.
    """

    top: Optional[int] = Field(default=None, ge=0, serialization_alias="$top")
    skip: Optional[int] = Field(default=None, ge=0, serialization_alias="$skip")
    search: Optional[str] = Field(default=None, serialization_alias="$search")
    filter: Optional[str] = Field(default=None, serialization_alias="$filter")
    count: Optional[bool] = Field(default=None, serialization_alias="$count")


class OrderbyParameters(QueryParameters):
    """
    Order items by property values

    Attributes:
        orderby (str): The field to order by.
    """

    orderby: Optional[str] = Field(default=None, serialization_alias="$orderby")


E = TypeVar("E", bound=Enum)


class SelectParameters(QueryParameters, Generic[E]):
    """
    Select properties to be returned

    Attributes:
        select (list): Select properties to be returned.
    """

    select: Optional[list[E]] = Field(default=None, serialization_alias="$select")


class ExpandParameters(QueryParameters):
    """Expand related entities

    Attributes:
        expand (str): Expand related entities.
    """

    expand: Optional[str] = Field(default=None, serialization_alias="$expand")
