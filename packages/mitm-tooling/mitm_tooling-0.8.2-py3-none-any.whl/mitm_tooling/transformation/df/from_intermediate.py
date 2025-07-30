import itertools

import pandas as pd

from mitm_tooling.data_types import convert
from mitm_tooling.definition import ConceptName, TypeName, get_mitm_def
from mitm_tooling.representation import mk_concept_file_header
from mitm_tooling.representation.df import MITMDataFrames
from mitm_tooling.representation.intermediate import Header, HeaderEntry, MITMData


def unpack_concept_table_as_typed_dfs(
    header: Header, concept: ConceptName, df: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    mitm_def = get_mitm_def(header.mitm)
    concept_properties, concept_relations = mitm_def.get(concept)

    with_header_entry: dict[tuple[str, TypeName], tuple[HeaderEntry, pd.DataFrame]] = {}
    if concept_properties.is_abstract:  # e.g. MAED.observation
        for (key, typ), idx in df.groupby(['kind', concept_properties.typing_concept]).groups.items():
            key, type_name = str(key), str(typ)
            specific_concept = mitm_def.inverse_concept_key_map[key]
            he = header.get(specific_concept, type_name)
            assert he is not None, 'missing type entry in header'
            with_header_entry[(specific_concept, type_name)] = (he, df.loc[idx])
    else:
        for typ, idx in df.groupby(concept_properties.typing_concept).groups.items():
            type_name = str(typ)
            he = header.get(concept, type_name)
            assert he is not None, 'missing type entry in header'
            with_header_entry[(concept, type_name)] = (he, df.loc[idx])

    res = {}
    for (concept, _type_name), (he, type_df) in with_header_entry.items():
        k = he.attr_k
        normal_form_cols, normal_form_dts = mk_concept_file_header(header.mitm, concept, k)
        type_df = type_df.reindex(columns=normal_form_cols)
        type_df = type_df.rename(columns=he.attr_name_map)
        dt_map = dict(
            itertools.chain(
                ((a, dt) for a, dt in normal_form_dts.items() if a in set(type_df.columns)), he.iter_attr_dtype_pairs()
            )
        )
        res[he.type_name] = convert.convert_df(type_df, dt_map)

    return res


def mitm_data_into_mitm_dataframes(mitm_data: MITMData) -> MITMDataFrames:
    mitm_data = mitm_data.as_specialized()
    return MITMDataFrames(
        header=mitm_data.header,
        dfs={concept: unpack_concept_table_as_typed_dfs(mitm_data.header, concept, df) for concept, df in mitm_data},
    )
