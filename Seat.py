class Seat:
    def __init__(self, row: int = None, column: int = None):
        self._row = row
        self._column = column

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, value: int):
        self._row = value

    @property
    def column(self) -> int:
        return self._column

    @column.setter
    def column(self, value: int):
        self._column = value
