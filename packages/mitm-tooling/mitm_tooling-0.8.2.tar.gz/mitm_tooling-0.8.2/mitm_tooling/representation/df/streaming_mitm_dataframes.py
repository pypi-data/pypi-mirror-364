from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import ConceptName, TypeName

from ..intermediate.header import Header
from .common import MitMDataFrameStream, TypedMitMDataFrameStream


class StreamingMITMDataFrames(Iterable[tuple[ConceptName, dict[TypeName, pd.DataFrame]]], pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    df_iters: dict[ConceptName, dict[TypeName, Iterable[pd.DataFrame]]]

    def __iter__(self):
        return iter(self.df_iters.items())

    def stream(self) -> MitMDataFrameStream:
        return ((c, ((t, df_iter) for t, df_iter in dfs.items())) for c, dfs in self.df_iters.items())

    def typed_stream(self) -> TypedMitMDataFrameStream:
        he_dict = self.header.as_dict
        return ((c, ((t, he_dict[c][t], df_iter) for t, df_iter in dfs.items())) for c, dfs in self.df_iters.items())
