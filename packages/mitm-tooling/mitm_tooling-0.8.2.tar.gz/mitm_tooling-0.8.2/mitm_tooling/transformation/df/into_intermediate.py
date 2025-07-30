from collections.abc import Iterable

import pandas as pd

from mitm_tooling.data_types import MITMDataType, convert
from mitm_tooling.definition import MITM, ConceptName
from mitm_tooling.representation import mk_concept_file_header
from mitm_tooling.representation.df import MITMDataFrames
from mitm_tooling.representation.intermediate import MITMData


def pack_typed_dfs_as_concept_table(mitm: MITM, concept: ConceptName, dfs: Iterable[pd.DataFrame]) -> pd.DataFrame:
    normalized_dfs = []
    for df in dfs:
        base_cols, col_dts = mk_concept_file_header(mitm, concept, 0)
        attr_cols = set(df.columns) - set(base_cols)
        k = len(attr_cols)
        normal_form_cols = list(base_cols) + list(attr_cols)
        df = df.reindex(columns=normal_form_cols)
        df = convert.convert_df(df, col_dts | {c: MITMDataType.Unknown for c in attr_cols})
        squashed_form_cols = mk_concept_file_header(mitm, concept, k)[0]
        df.columns = squashed_form_cols
        normalized_dfs.append((df, k))

    assert len(normalized_dfs) > 0
    max_k = max(normalized_dfs, key=lambda x: x[1])[1]

    squashed_form_cols = mk_concept_file_header(mitm, concept, max_k)[0]
    return pd.concat([df for df, _ in normalized_dfs], axis='rows', ignore_index=True).reindex(
        columns=squashed_form_cols
    )


def mitm_dataframes_into_mitm_data(mitm_dataset: MITMDataFrames) -> MITMData:
    return MITMData(
        header=mitm_dataset.header,
        concept_dfs={
            concept: pack_typed_dfs_as_concept_table(mitm_dataset.header.mitm, concept, typed_dfs.values())
            for concept, typed_dfs in mitm_dataset
            if len(typed_dfs) > 1
        },
    ).as_generalized()
