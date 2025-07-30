import itertools
from collections.abc import Iterator

import pandas as pd
import pydantic
import sqlalchemy as sa
from pydantic import ConfigDict

from mitm_tooling.definition import MITM, ConceptName, get_mitm_def
from mitm_tooling.io import StreamingZippedExport, ZippedExport
from mitm_tooling.representation.common import mk_concept_file_header
from mitm_tooling.representation.intermediate import (
    Header,
    HeaderEntry,
    MITMData,
    StreamingConceptData,
    StreamingMITMData,
)
from mitm_tooling.utilities.sql_utils import AnyDBBind

from ..data_models import DBMetaInfo, SourceDBType, TableIdentifier, VirtualView
from ..transformation import PostProcessing
from ..transformation.db_transformation import TableNotFoundException
from .concept_mapping import (
    ConceptMapping,
    ConceptMappingException,
    DataProvider,
    InstancesPostProcessor,
    InstancesProvider,
)

STREAMING_CHUNK_SIZE = 100_000


class Exportable(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    data_providers: dict[ConceptName, list[DataProvider]]
    filename: str | None = None

    def generate_header(self, bind: AnyDBBind) -> Header:
        header_entries = []
        for _, dps in self.data_providers.items():
            for dp in dps:
                header_entries.extend(dp.header_entry_provider.apply_db(bind))
        return Header(mitm=self.mitm, header_entries=frozenset(header_entries))

    @property
    def generalized_data_providers(self) -> dict[ConceptName, list[DataProvider]]:
        mitm_def = get_mitm_def(self.mitm)

        temp = {}
        for c, dps in self.data_providers.items():
            main_concept = mitm_def.get_parent(c)
            if main_concept not in temp:
                temp[main_concept] = []
            temp[main_concept].extend(dps)

        return temp

    def export_to_memory(self, bind: AnyDBBind, validate: bool = False) -> ZippedExport:
        header_entries = []

        tables = {}
        for c, dps in self.generalized_data_providers.items():
            dfs = []
            for dp in dps:
                df = dp.instance_provider.apply_db(bind)
                if validate:
                    raise NotImplementedError
                df = dp.instance_postprocessor.apply_df(df)
                dfs.append(df)
                header_entries += dp.header_entry_provider.apply_df(df)

            tables[c] = pd.concat(dfs, axis='index', ignore_index=True)

        header = Header(mitm=self.mitm, header_entries=frozenset(header_entries))

        filename = self.filename if self.filename else f'{self.mitm}.zip'

        return ZippedExport(mitm=self.mitm, filename=filename, mitm_data=MITMData(header=header, concept_dfs=tables))

    def export_as_stream(self, bind: AnyDBBind, validate: bool = False) -> StreamingZippedExport:
        data_sources = {}

        for main_concept, dps in self.generalized_data_providers.items():
            k = max(dp.header_entry_provider.type_arity for dp in dps)
            concept_file_columns = mk_concept_file_header(self.mitm, main_concept, k)[0]
            structure_df = pd.DataFrame(columns=concept_file_columns)

            chunk_iterators = []
            for dp in dps:

                def local_iter(
                    dp: DataProvider = dp, columns=tuple(concept_file_columns)
                ) -> Iterator[tuple[pd.DataFrame, list[HeaderEntry]]]:
                    for df_chunk in dp.instance_provider.apply_db_chunked(bind, STREAMING_CHUNK_SIZE):
                        if validate:
                            raise NotImplementedError
                        df_chunk = dp.instance_postprocessor.apply_df(df_chunk)
                        hes = dp.header_entry_provider.apply_df(df_chunk)
                        # this does nothing more than adding NaN columns to fill up to the number of attributes in the concept file (k)
                        df_chunk = df_chunk.reindex(columns=list(columns), copy=False)
                        yield df_chunk, hes

                chunk_iterators.append(local_iter())

            data_sources[main_concept] = StreamingConceptData(
                structure_df=structure_df, chunk_iterators=chunk_iterators
            )

        filename = self.filename if self.filename else f'{self.mitm}.zip'
        return StreamingZippedExport(
            mitm=self.mitm,
            filename=filename,
            streaming_mitm_data=StreamingMITMData(mitm=self.mitm, data_sources=data_sources),
        )


class MappingExport(pydantic.BaseModel):
    mitm: MITM
    concept_mappings: list[ConceptMapping]
    post_processing: PostProcessing | None = None
    filename: str | None = None

    def apply(self, db_metas: dict[SourceDBType, DBMetaInfo]) -> Exportable:
        data_providers: dict[ConceptName, list[DataProvider]] = {}

        meta = sa.MetaData(schema='export')
        for i, concept_mapping in enumerate(self.concept_mappings):
            if concept_mapping.mitm != self.mitm:
                continue

            try:
                header_entry_provider, q = concept_mapping.apply(db_metas)
            except TableNotFoundException as e:
                raise ConceptMappingException('Concept Mapping failed.') from e

            # mitm_def = get_mitm_def(self.mitm)
            # main_concept = mitm_def.get_parent(concept_mapping.concept)
            concept = concept_mapping.concept

            vv = VirtualView.from_from_clause(f'{concept}_{i}', q, meta, schema='export')
            instances_provider = InstancesProvider(virtual_view=vv)

            pp_transforms = []
            if self.post_processing is not None:
                pp_transforms = list(
                    itertools.chain(
                        tpp.transforms
                        for tpp in self.post_processing.table_postprocessing
                        if TableIdentifier.check_equal(tpp.target_table, concept_mapping.base_table)
                    )
                )
            post_processor = InstancesPostProcessor(transforms=pp_transforms)

            if concept not in data_providers:
                data_providers[concept] = []
            data_providers[concept].append(
                DataProvider(
                    instance_provider=instances_provider,
                    instance_postprocessor=post_processor,
                    header_entry_provider=header_entry_provider,
                )
            )

        return Exportable(mitm=self.mitm, data_providers=data_providers, filename=self.filename)
