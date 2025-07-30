from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import Self

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import MITM, ConceptName
from mitm_tooling.utilities.python_utils import take_first

from ..intermediate.header import HeaderEntry


class StreamingConceptData(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    structure_df: pd.DataFrame
    chunk_iterators: list[Iterator[tuple[pd.DataFrame, list[HeaderEntry]]]] = pydantic.Field(default_factory=list)


class StreamingMITMData(Iterable[tuple[ConceptName, StreamingConceptData]], pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    data_sources: dict[ConceptName, StreamingConceptData] = pydantic.Field(default_factory=dict)

    def __iter__(self):
        return iter(self.data_sources.items())

    def as_generalized(self) -> Self:
        mitm_def = get_mitm_def(self.mitm)
        combined_data_sources = defaultdict(list)
        for c, ds in self:
            combined_data_sources[mitm_def.get_parent(c)].append(ds)
        data_sources = {}
        for c, ds_list in combined_data_sources.items():
            structure_dfs = [ds.structure_df for ds in ds_list]
            assert all(a.equals(b) for a, b in zip(structure_dfs[:-1], structure_dfs[1:], strict=False)), (
                f'concept {c} not generalizable in {self} (structure_dfs differ)'
            )
            data_sources[c] = StreamingConceptData(
                structure_df=take_first(structure_dfs),
                chunk_iterators=[it for ds in ds_list for it in ds.chunk_iterators],
            )
        return StreamingMITMData(mitm=self.mitm, data_sources=data_sources)
