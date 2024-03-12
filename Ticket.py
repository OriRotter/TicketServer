import uuid
import sqlite3
import os
from Seat import Seat  # Assuming Seat is defined in a separate module


class Ticket:
    def __init__(self, order_number, show_id, ticket_num, seat=Seat()):
        self._show_id = show_id
        self._order_number = order_number
        self._seat = seat
        self._hash = self._create_hash()
        self._ticket_num = ticket_num
        self._used = False

    def __str__(self):
        return f"This ticket hash is {self._hash}. He is sitting in {self._seat.place} at {self._seat.row}x{self._seat.column}. Ticket number {self._ticket_num}. "

    def use(self):
        self._used = True
        self.update_ticket()

    def update_ticket(self):
        db_path = f"Databases/{self._show_id}/{self._show_id}-hashes.db"
        if not os.path.exists(db_path):
            raise ValueError("No such show ID.")

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE Tickets SET 
                              Used = ?,
                              Place = ?,
                              Row = ?,
                              Column = ?,
                              OrderNumber = ?,
                              TicketNumber = ?
                              WHERE Hash = ?''',
                           (self._used, self._seat.place, self._seat.row, self._seat.column,
                            self._order_number, self._ticket_num, self._hash))
            conn.commit()


    def store_ticket(self):
        db_path = f"Databases/{self._show_id}/{self._show_id}-hashes.db"
        if not os.path.exists(db_path):
            raise ValueError("No such show ID.")

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Tickets (OrderNumber, Place, Row, Column, TicketNumber, Used, Hash)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (self._order_number, self._seat.place, self._seat.row, self._seat.column,
                            self._ticket_num, self._used, self._hash))
            conn.commit()

    def is_used(self):
        return self._used

    def _create_hash(self):
        unique_id = uuid.uuid4()
        return str(unique_id)

    # Property definitions
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
