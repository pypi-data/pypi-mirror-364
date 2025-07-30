import pandas as pd

from mitm_tooling.utilities.io_utils import DataSink, FilePath, ensure_directory_exists


def write_header_file(df: pd.DataFrame, sink: DataSink | None) -> str | None:
    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    return df.to_csv(sink, header=True, index=False, sep=';')


def write_data_file(df: pd.DataFrame, sink: DataSink | None, append: bool = False) -> str | None:
    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    return df.to_csv(sink, header=not append, index=False, sep=';', date_format='%Y-%m-%dT%H:%M:%S.%f%z')
