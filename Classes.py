import uuid
import sqlite3
from Strings import *


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
        db_path = hash_path(showID=self._show_id)
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
        db_path = hash_path(showID=self._show_id)
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


class TicketGroup:
    def __init__(self, show_id, seats, phone_number, email, name=None):
        self._show_id = show_id
        self._name = name
        if '05' not in phone_number:
            raise ValueError("Invalid phone number")
        self._phone_number = phone_number
        if '@' not in email:
            raise ValueError("Invalid email")
        self._email = email
        self._order_number = self._get_order_number()
        self._tickets = []
        self._ticket_number = self._get_ticket_number()

        for seat in seats:
            ticket = Ticket(self._order_number, self._show_id, self._ticket_number, seat)
            self._tickets.append(ticket)
            self._ticket_number += 1

        self._store_order()
        self._store_hashes()

    def _get_ticket_number(self):
        try:
            with sqlite3.connect(hash_path(showID=self._show_id)) as conn:
                cursor = conn.cursor()
                max_ticket_number = cursor.execute("SELECT MAX(TicketNumber) FROM Tickets").fetchone()[0]
                return max_ticket_number + 1 if max_ticket_number is not None else 1
        except:
            raise ValueError("No such show")

    def _get_order_number(self):
        try:
            with sqlite3.connect(order_path(showID=self._show_id)) as conn:
                cursor = conn.cursor()
                max_order_number = cursor.execute("SELECT MAX(OrderNumber) FROM Orders").fetchone()[0]
                return max_order_number + 1 if max_order_number is not None else 1
        except:
            raise ValueError("No such show")

    def _store_order(self):
        with sqlite3.connect(order_path(showID=self._show_id)) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Orders (OrderNumber, Name, Email, PhoneNumber)
                                          VALUES (?, ?, ?, ?)''',
                           (self._order_number, self._name, self._email, self._phone_number))
            conn.commit()

    def _store_hashes(self):
        for ticket in self._tickets:
            ticket.store_ticket()

    def get_tickets(self):
        ticket_info = {}
        for ticket in self._tickets:
            ticket_info[f"{ticket.hash},{ticket.show_id}"] = [
                ticket.order_number, ticket.place, ticket.row, ticket.column, ticket.ticket_num, bool(ticket._used)]
        return ticket_info

    def updateOrder(self):
        # Update the specified order in the database with new information
        db_path = order_path(showID=self._show_id)
        if not os.path.exists(db_path):
            raise ValueError("No such show ID.")

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE Orders SET
                                 PhoneNumber = ?,
                                 Email = ?,
                                 Name = ?
                                 WHERE OrderNumber = ?''',
                           (self._phone_number, self._email, self._name, self._order_number,))

            conn.commit()
