from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Self

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from mitm_tooling.definition import MITM
from mitm_tooling.representation.sql import Queryable

from ..data_models import DBMetaInfo, SourceDBType, VirtualDB
from ..transformation import VirtualDBCreation
from .concept_mapping import ConceptMapping

if TYPE_CHECKING:
    from .export import Exportable


class ExecutableDBMapping(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    db_metas: dict[SourceDBType, DBMetaInfo]
    concept_mappings: list[ConceptMapping]

    def to_exportable(self, filename: str | None = None) -> Exportable:
        from .export import MappingExport

        return MappingExport(mitm=self.mitm, concept_mappings=self.concept_mappings, filename=filename).apply(
            self.db_metas
        )


class DBMapping(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    concept_mappings: list[ConceptMapping]

    @model_validator(mode='after')
    def post_val(self) -> Self:
        if any(cm.mitm != self.mitm for cm in self.concept_mappings):
            raise ValidationError('All mappings must belong to the same MitM')
        return self


class StandaloneDBMapping(DBMapping):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    virtual_db_creation: VirtualDBCreation

    def recreate_virtual_db(
        self, remote_engine: sa.Engine, queryable_verifier: Callable[[Queryable], bool] | None = None
    ) -> tuple[VirtualDB, dict[SourceDBType, DBMetaInfo]]:
        from mitm_tooling.transformation.sql import db_engine_into_db_meta

        original_db_meta = db_engine_into_db_meta(remote_engine)
        vdb = self.virtual_db_creation.apply(original_db_meta, queryable_verifier=queryable_verifier)
        return vdb, {SourceDBType.OriginalDB: original_db_meta, SourceDBType.VirtualDB: vdb.to_db_meta_info()}

    def to_exportable(self, remote_engine: sa.Engine, filename: str | None = None) -> Exportable:
        from .export import MappingExport

        _, db_metas = self.recreate_virtual_db(remote_engine)
        return MappingExport(mitm=self.mitm, concept_mappings=self.concept_mappings, filename=filename).apply(db_metas)
