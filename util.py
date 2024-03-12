import os
import sqlite3
from TicketGroup import TicketGroup


def use_hash(show_id, ticket_hash):
    if not os.path.exists(f"Databases/{show_id}/{show_id}-hashes.db"):
        raise ValueError("No such show ID.")

    with sqlite3.connect(f"Databases/{show_id}/{show_id}-hashes.db") as conn:
        cursor = conn.cursor()
        used = cursor.execute('SELECT 1 FROM Tickets WHERE Row = 2 AND Column = 2', (ticket_hash,)).fetchone()

        if used is None:
            return "404 no such hash."

        if not used[0]:
            cursor.execute('UPDATE Tickets SET Used = 1 WHERE Hash = ?', (ticket_hash,))
            conn.commit()
            return "200 OK"

        return "300 Hash used."


def check_seat(show_id, seat):
    if not os.path.exists(f"Databases/{show_id}/{show_id}-hashes.db"):
        raise ValueError("No such show ID.")

    with sqlite3.connect(f"Databases/{show_id}/{show_id}-hashes.db") as conn:
        cursor = conn.cursor()
        check = cursor.execute('SELECT 1 FROM Tickets WHERE Row = ? AND Column = ? AND Place = ?',
                               (seat.row, seat.column, seat.place)).fetchone()

        if check is None:
            return True
        return False


def get_info_by_hash(show_id, ticket_hash):
    if not os.path.exists(f"Databases/{show_id}/{show_id}-hashes.db"):
        raise ValueError("No such show ID.")

    with sqlite3.connect(f"Databases/{show_id}/{show_id}-hashes.db") as conn:
        cursor = conn.cursor()
        ticket_info = cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE Hash = ?''', (ticket_hash,)).fetchone()

        if ticket_info is None:
            return "404 no such hash."

        return ticket_info


def get_info_by_ticket_number(show_id, ticket_num):
    if not os.path.exists(f"Databases/{show_id}/{show_id}-hashes.db"):
        raise ValueError("No such show ID.")

    with sqlite3.connect(f"Databases/{show_id}/{show_id}-hashes.db") as conn:
        cursor = conn.cursor()
        ticket_info = cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE TicketNumber = ?''', (ticket_num,)).fetchone()

        if ticket_info is None:
            return "404 no such ticket number."

        return ticket_info


def create_tickets(show_id, seats, phone_number, email, name=None):
    for seat in seats:
        if not check_seat(show_id=show_id,seat=seat):
            raise ValueError("Seat is taken.")
    tickets = TicketGroup(show_id=show_id, seats=seats, phone_number=phone_number, email=email, name=name)
    return tickets.get_tickets()
