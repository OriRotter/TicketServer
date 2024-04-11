from Seat import Seat
import uuid


def _create_hash():
    unique_id = uuid.uuid4()
    return str(unique_id)


class Ticket:
    def __init__(self, order_number, show_id, ticket_num, seat=Seat()):
        self._show_id = show_id
        self._order_number = order_number
        self._seat = seat
        self._hash = _create_hash()
        self._ticket_num = ticket_num
        self._used = False

    def __str__(self):
        return f"This ticket hash is {self._hash}. He is sitting in {self._seat.place} at {self._seat.row}x{self._seat.column}. Ticket number {self._ticket_num}. "

    # Property definitions
    @property
    def used(self):
        return self._used

    @property
    def row(self):
        return self._seat.row

    @row.setter
    def row(self, value):
        self._seat.row = value

    @property
    def column(self):
        return self._seat.column

    @column.setter
    def column(self, value):
        self._seat.column = value

    @property
    def place(self):
        return self._seat.place

    @place.setter
    def place(self, value):
        self._seat.place = value

    @property
    def hash(self):
        return self._hash

    @property
    def ticket_num(self):
        return self._ticket_num

    @ticket_num.setter
    def ticket_num(self, value):
        self._ticket_num = value

    @property
    def order_number(self):
        return self._order_number

    @order_number.setter
    def order_number(self, value):
        self._order_number = value

    @property
    def show_id(self):
        return self._show_id

    @show_id.setter
    def show_id(self, value):
        self._show_id = value
