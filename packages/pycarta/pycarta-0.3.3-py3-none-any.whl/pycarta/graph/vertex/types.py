from __future__ import annotations

from datetime import datetime
import json
import numpy as np
import pandas as pd

from abc import ABC
from collections.abc import Hashable, MutableMapping
from copy import deepcopy
# from pycarta.graph.util import as_list
from pydantic import BaseModel, Field, model_validator
from typing import Any, TypeAlias, Union
from uuid import uuid4, UUID


__all__ = ["Vertex", "DictVertex"]


JsonScalarType: TypeAlias = Union[int, float, str, bool, None]
JsonType: TypeAlias = Union[JsonScalarType, list[Any], dict[str, Any]]


class NumpyDateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o) # pragma: no cover


class Vertex(BaseModel, ABC, Hashable):
    id: UUID=Field(default_factory=uuid4)

    def __hash__(self) -> int:
        return self.id.int
    
    def copy(self, *, update: dict[str, Any] | None = None, deep: bool = False) -> "Vertex": # type: ignore
        """
        Returns a copy of the vertex.

        Parameters
        ----------
        update : dict
            Values to change/add in the new Vertex. Note: the data is not
            validated before creating the new Vertex. You should trust this
            data.

        deep : bool
            Set to True to make a deep copy of the model.

        Returns
        -------
        Vertex
            New Vertex instance.
        """
        result = self.model_copy(update=update, deep=deep)
        result.id = uuid4()
        return result


class DictVertex(Vertex, MutableMapping):
    content_ : dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode="before")
    @classmethod
    def preprocess_constructor_args(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Preprocess the constructor arguments. Dict-like content passed as the
        `content_` keyword to the contructor bypasses the JSON-serialization
        test.

        Parameters
        ----------
        data : dict
            The data to be used to construct the instance.

        Returns
        -------
        dict
            The preprocessed data.
        """
        id_ = data.pop("id", None)
        content = data.pop("content_", None)
        content = content or json.loads(json.dumps(data, cls=NumpyDateTimeEncoder))
        data = {"content_": content} | ({"id": id_} if id_ is not None else {})
        return data

    def __len__(self):
        return len(self.content_)

    def __getitem__(self, key):
        return self.content_[key]

    def __setitem__(self, key, value):
        self.content_[key] = value

    def __delitem__(self, key):
        del self.content_[key]

    def __iter__(self): # type: ignore
        return self.content_.__iter__()

    def __hash__(self) -> int:
        return super().__hash__()
    
    def __eq__(self, rhs: dict | DictVertex) -> bool: # type: ignore
        if isinstance(rhs, DictVertex):
            return self.content_ == rhs.content_
        else:
            return self.content_ == rhs
        
    def __ne__(self, rhs: dict | DictVertex) -> bool: # type: ignore
        return not self == rhs
        
    def __req__(self, lhs: dict | DictVertex) -> bool:  # pragma: no cover
        # Equality is commutative
        return self == lhs
    
    def __rne__(self, lhs: dict | DictVertex) -> bool:  # pragma: no cover
        # Equality is commutative
        return not self == lhs
    
    @classmethod
    def from_json(cls, obj: JsonType) -> Vertex:
        if not isinstance(obj, dict):
            raise TypeError(f"Expected a dict, got {type(obj)}")
        return cls(**obj)
    
    def to_json(self) -> JsonType:
        return self.content_
    
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.content_)
    
    def copy(self, vertex: dict | DictVertex | None = None, /) -> DictVertex: # type: ignore
        """
        Either returns a copy of the current vertex (no positional parameter) or
        copies the contents of the argument into the current vertex.
        """
        # If nothing is specified, we're copying the current instance.
        if vertex is None:
            return type(self)(content_ = deepcopy(self.content_))
        # If we get here, we're copying content into this instance
        if isinstance(vertex, DictVertex):
            self.content_ = deepcopy(vertex.content_)
        else:
            self.content_ = json.loads(json.dumps(vertex, cls=NumpyDateTimeEncoder))
        return self
