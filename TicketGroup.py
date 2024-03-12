import sqlite3
from Ticket import Ticket  # Assuming Ticket is defined in a separate module
import os


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
            with sqlite3.connect(f"Databases/{self._show_id}/{self._show_id}-hashes.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS Tickets (
                                "OrderNumber" INTEGER NOT NULL,
                                "Place" TEXT,
                                "Row" INTEGER,
                                "Column" INTEGER,
                                "TicketNumber" INTEGER NOT NULL,
                                "Used" BOOLEAN NOT NULL,
                                "Hash" TEXT NOT NULL
                                  )''')
                max_ticket_number = cursor.execute("SELECT MAX(TicketNumber) FROM Tickets").fetchone()[0]
                return max_ticket_number + 1 if max_ticket_number is not None else 1
        except:
            raise ValueError("No such show")

    def _get_order_number(self):
        try:
            with sqlite3.connect(f"Databases/{self._show_id}/{self._show_id}-orders.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
                                "OrderNumber" INTEGER NOT NULL,
                                "Name" TEXT,
                                "Email" TEXT NOT NULL,
                                "PhoneNumber" TEXT NOT NULL
                                  )''')
                max_order_number = cursor.execute("SELECT MAX(OrderNumber) FROM Orders").fetchone()[0]
                return max_order_number + 1 if max_order_number is not None else 1
        except:
            raise ValueError("No such show")

    def _store_order(self):
        with sqlite3.connect(f"Databases/{self._show_id}/{self._show_id}-orders.db") as conn:
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
                ticket.order_number, ticket.place, ticket.row, ticket.column,ticket.ticket_num,bool(ticket._used)]
        return ticket_info

    def updateOrder(self):
        # Update the specified order in the database with new information
        db_path = f"Databases/{self._show_id}/{self._show_id}-orders.db"
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
