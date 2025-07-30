from contextlib import contextmanager
from typing import Iterator, List

import duckdb

from ipydb.base import BaseDatabase, BaseSchema, BaseTable


class DuckdbTable(BaseTable):
    def get(self):
        with _yield_duckdb(self) as con:
            df = con.execute(f"SELECT * FROM {self.schema_table};").fetch_df()

        return df

    def drop(self):
        with _yield_duckdb(self) as con:
            _ = con.execute(f"DROP TABLE {self.schema_table};")

    def load(self):
        self.global_vars[self.table] = self.get()


class DuckdbSchema(BaseSchema):
    _table_cls = DuckdbTable

    def _list_tables(self) -> List[str]:
        with _yield_duckdb(self) as con:
            df = con.execute(
                f"SELECT name FROM (SHOW ALL TABLES) WHERE schema = '{self._schema}';"
            ).fetch_df()

        return df["name"].tolist()


class DuckdbDatabase(BaseDatabase):
    _schema_cls = DuckdbSchema

    def __init__(self, conn_str: str, global_vars):
        return super().__init__(global_vars, duckdb.connect, database=conn_str)

    def _list_schemas(self) -> List[str]:
        with _yield_duckdb(self) as con:
            df = con.execute("SHOW ALL TABLES;").fetch_df()

        return df["schema"].unique().tolist()


@contextmanager
def _yield_duckdb(
    self: DuckdbTable | DuckdbSchema | DuckdbDatabase,
) -> Iterator[duckdb.DuckDBPyConnection]:
    with self._connection_fn(**self._connection_kwargs) as con:
        yield con
