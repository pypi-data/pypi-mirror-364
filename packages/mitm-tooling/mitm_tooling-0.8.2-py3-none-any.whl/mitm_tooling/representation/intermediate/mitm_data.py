from collections import defaultdict
from collections.abc import Iterable
from typing import Self

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import ConceptName

from ..intermediate.header import Header


class MITMData(Iterable[tuple[ConceptName, pd.DataFrame]], pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    concept_dfs: dict[ConceptName, pd.DataFrame] = pydantic.Field(default_factory=dict)

    def __iter__(self):
        return iter(self.concept_dfs.items())

    def as_generalized(self) -> Self:
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = defaultdict(list)
        for c, df in self.concept_dfs.items():
            c = mitm_def.get_parent(c)
            dfs[c].append(df)
        dfs = {c: pd.concat(dfs_, axis='rows', ignore_index=True) for c, dfs_ in dfs.items()}
        return MITMData(header=self.header, concept_dfs=dfs)

    def as_specialized(self) -> Self:
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = {}
        for c, df in self:
            if mitm_def.get_properties(c).is_abstract:
                # leaf_concepts = mitm_def.get_leafs(c)

                for sub_c_key, idx in df.groupby('kind').groups.items():
                    sub_c = mitm_def.inverse_concept_key_map[str(sub_c_key)]
                    dfs[sub_c] = df.loc[idx]
            else:
                dfs[c] = df
        return MITMData(header=self.header, concept_dfs=dfs)
