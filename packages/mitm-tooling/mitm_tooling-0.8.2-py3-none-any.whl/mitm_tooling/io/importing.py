import glob
import logging
import os.path
import zipfile
from abc import ABC, abstractmethod

import pydantic

from mitm_tooling.definition import MITM, get_mitm_def
from mitm_tooling.representation.file import read_data_file, read_header_file
from mitm_tooling.representation.intermediate import Header, MITMData
from mitm_tooling.utilities.io_utils import DataSource, FilePath, ensure_ext, use_bytes_io, use_for_pandas_io

logger = logging.getLogger('api')


class FileImport(pydantic.BaseModel, ABC):
    mitm: MITM
    filename: str | None = None

    @abstractmethod
    def read(self, source: DataSource, **kwargs) -> MITMData | None:
        pass


class ZippedImport(FileImport):
    def read(self, source: DataSource, header_only: bool = False, **kwargs) -> MITMData | None:
        mitm_def = get_mitm_def(self.mitm)
        with use_bytes_io(source, expected_file_ext='.zip', mode='rb') as f:
            parts = {}
            with zipfile.ZipFile(f, 'r', compression=zipfile.ZIP_DEFLATED) as zf:
                with zf.open('header.csv') as h:
                    parts['header'] = read_header_file(h, normalize=True)
                files_in_zip = set(zf.namelist())
                if not header_only:
                    for concept in mitm_def.main_concepts:
                        fn = ensure_ext(mitm_def.get_properties(concept).plural, '.csv')
                        if fn in files_in_zip:
                            with zf.open(fn) as cf:
                                parts[concept] = read_data_file(
                                    cf, target_mitm=self.mitm, target_concept=concept, normalize=True
                                )
            assert 'header' in parts
            return MITMData(header=Header.from_df(parts.pop('header'), self.mitm), concept_dfs=parts)


class FolderImport(FileImport):
    def read(self, source: DataSource, header_only: bool = False, **kwargs) -> MITMData | None:
        assert isinstance(source, FilePath)
        assert os.path.exists(source)

        file_names = glob.glob('*.csv', root_dir=source)
        mitm_def = get_mitm_def(self.mitm)

        parts = {}
        file_names.remove('header.csv')
        with use_for_pandas_io('header.csv') as f:
            parts['header'] = read_header_file(f, normalize=True)

        if not header_only:
            for concept in mitm_def.main_concepts:
                fn = ensure_ext(mitm_def.get_properties(concept).plural, '.csv')
                if fn in file_names:
                    parts[concept] = read_data_file(fn, target_mitm=self.mitm, target_concept=concept, normalize=True)

        return MITMData(header=Header.from_df(parts.pop('header'), self.mitm), concept_dfs=parts)


def read_zip(source: DataSource, mitm: MITM | None = None, header_only: bool = False, **kwargs) -> MITMData | None:
    filename = None
    if isinstance(source, FilePath):
        filename = source
        _, ext = os.path.splitext(source)
        if not mitm:
            try:
                mitm = MITM(ext[1:].upper())
            except ValueError:
                pass
    if mitm:
        return ZippedImport(mitm=mitm, filename=filename).read(source, header_only=header_only, **kwargs)
    else:
        logger.error('Attempted to import data with unspecified MitM.')
