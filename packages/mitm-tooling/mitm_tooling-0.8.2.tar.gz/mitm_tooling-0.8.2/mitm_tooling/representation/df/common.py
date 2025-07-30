from collections.abc import Iterable

import pandas as pd

from mitm_tooling.definition import ConceptName, TypeName

from ..intermediate.header import HeaderEntry

MitMDataFrameStream = Iterable[tuple[ConceptName, Iterable[tuple[TypeName, Iterable[pd.DataFrame]]]]]
TypedMitMDataFrameStream = Iterable[tuple[ConceptName, Iterable[tuple[TypeName, HeaderEntry, Iterable[pd.DataFrame]]]]]
