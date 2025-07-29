from sqlalchemy.orm import Query
from dozersim.suppliers import session
from dozersim.modelling import Settings


class DatabaseLink:
    """
    Adapter that couples settings (Settings) to a database table

    """

    def __init__(self, settings: Settings):
        self._settings: Settings = settings
        if settings.supplier_table:
            self._table = settings.supplier_table
        else:
            raise Exception("No supplier table linked to this setting class! Implement the supplier_table getter "
                            "method.")
        self._query: Query
        self.reset_query()

    def __iter__(self):
        return self._query.__iter__()

    def list_table(self):
        for entry in self._query:
            print(f"Table entry {entry.name}")

    def set_value(self, value: Query | str | Settings):
        while True:
            if type(value) is str:
                value = self._query.filter_by(name=value).first()
            else:
                for attr in [val for val in value.__dict__.keys() if '_sa_' not in val]:
                    setattr(self._settings, attr, getattr(value, attr))
                break

    @property
    def query(self) -> Query:
        return self._query

    @query.setter
    def query(self, query: Query):
        self._query = query

    def reset_query(self):
        self._query = session.query(self._table)

