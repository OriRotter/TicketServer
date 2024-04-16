import sqlite3
from Strings import *
from cryptography.fernet import Fernet
def encrypt_db(show_id,KEY = KEY):
    hash = hash_path(show_id)
    order = order_path(show_id)
    key = KEY
    f = Fernet(key)
    with open(hash, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(hash, "wb") as file:
        file.write(encrypted_data)

    with open(order, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(order, "wb") as file:
        file.write(encrypted_data)

def decrypt_db(show_id,KEY = KEY):
    hash = hash_path(show_id)
    order = order_path(show_id)
    f = Fernet(KEY)
    with open(hash, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = f.decrypt(encrypted_data)
    with open(hash, "wb") as file:
        file.write(decrypted_data)

    with open(order, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = f.decrypt(encrypted_data)
    with open(order, "wb") as file:
        file.write(decrypted_data)


def use_hash(show_id, ticket_hash):
    db_path = hash_path(showID=show_id)
    if not os.path.exists(db_path):
        raise ValueError("No such show ID.")


    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        used = cursor.execute('SELECT Used FROM Tickets WHERE Hash = ?', (ticket_hash,)).fetchone()

        if used is None:
            return "404 no such hash."

        if not used[0]:
            cursor.execute('UPDATE Tickets SET Used = 1 WHERE Hash = ?', (ticket_hash,))
            conn.commit()
            return "200 OK"

        return "300 Hash used."


def check_seat(show_id, seat):
    db_path = hash_path(showID=show_id)
    if not os.path.exists(db_path):
        raise ValueError("No such show ID.")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        check = cursor.execute('SELECT 1 FROM Tickets WHERE Row = ? AND Column = ? AND Place = ?',
                               (seat.row, seat.column, seat.place)).fetchone()

        return check is None


def get_info_by_hash(show_id, ticket_hash):
    db_path = hash_path(showID=show_id)
    if not os.path.exists(db_path):
        raise ValueError("No such show ID.")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        ticket_info = cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE Hash = ?''', (ticket_hash,)).fetchone()

        return ticket_info or "404 no such hash."


def get_info_by_something(show_id, something):
    db_path = hash_path(showID=show_id)
    if not os.path.exists(db_path):
        raise ValueError("No such show ID.")

    ticket_info = []
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            ticket_info += cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                            FROM Tickets WHERE OrderNumber = ? OR TicketNumber = ? OR Hash = ? ''',
                                          (something, something, something)).fetchone()
        except sqlite3.Error:
            pass

    order_db_path = order_path(showID=show_id)
    if not os.path.exists(order_db_path):
        raise ValueError("No such show ID.")

    with sqlite3.connect(order_db_path) as conn:
        cursor = conn.cursor()
        try:
            ticket_info += cursor.execute('''SELECT OrderNumber, Name, Email, PhoneNumber
                                            FROM Orders WHERE OrderNumber = ? OR Name = ? OR Email = ? OR PhoneNumber = ? ''',
                                          (something, something, something, something)).fetchone()
        except sqlite3.Error:
            pass

    return ticket_info or f"404 no such {something}."


def get_info_by_ticket_number(show_id, ticket_num):
    db_path = hash_path(showID=show_id)
    if not os.path.exists(db_path):
        raise ValueError("No such show ID.")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        ticket_info = cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE TicketNumber = ?''', (ticket_num,)).fetchone()

        return ticket_info or "404 no such ticket number."


def store_ticket(ticket):
    db_path = hash_path(showID=ticket.show_id)
    if not os.path.exists(db_path):
        raise ValueError("No such show ID.")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Tickets (OrderNumber, Place, Row, Column, TicketNumber, Used, Hash)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (ticket.order_number, ticket.place, ticket.row, ticket.column,
                        ticket.ticket_num, ticket.used, ticket.hash))
        conn.commit()


def get_ticket_number(ticketGroup):
    db_path = hash_path(showID=ticketGroup.show_id)
    if not os.path.exists(db_path):
        raise ValueError("No such show ID.")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        max_ticket_number = cursor.execute("SELECT MAX(TicketNumber) FROM Tickets").fetchone()[0]
        return (max_ticket_number or 0) + 1


def get_order_number(ticketGroup):
    order_db_path = order_path(showID=ticketGroup.show_id)
    if not os.path.exists(order_db_path):
        raise ValueError("No such show ID.")

    with sqlite3.connect(order_db_path) as conn:
        cursor = conn.cursor()
        max_order_number = cursor.execute("SELECT MAX(OrderNumber) FROM Orders").fetchone()[0]
        return (max_order_number or 0) + 1


def store_order(ticketGroup):
    order_db_path = order_path(showID=ticketGroup.show_id)
    with sqlite3.connect(order_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Orders (OrderNumber, Name, Email, PhoneNumber)
                                      VALUES (?, ?, ?, ?)''',
                       (ticketGroup.order_number, ticketGroup.name, ticketGroup.email, ticketGroup.phone_number))
        conn.commit()


def store_hashes(ticketGroup):
    for ticket in ticketGroup.tickets:
        store_ticket(ticket)


def get_tickets(ticketGroup):
    ticket_info = {}
    for ticket in ticketGroup.tickets:
        ticket_info[f"{ticket.hash},{ticket.show_id}"] = [
            ticket.order_number, ticket.place, ticket.row, ticket.column, ticket.ticket_num, bool(ticket._used)]
    return ticket_info
