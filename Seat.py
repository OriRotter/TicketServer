class Seat:
    def __init__(self, place: str = None, row: int = None, column: int = None):
        self._place = place
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

    @property
    def place(self) -> str:
        return self._place

    @place.setter
    def place(self, value: str):
        self._place = value
