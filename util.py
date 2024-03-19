from Classes import *
from Strings import *


def use_hash(show_id, ticket_hash):
    if not os.path.exists(hash_path(showID=show_id)):
        raise ValueError("No such show ID.")

    with sqlite3.connect(hash_path(showID=show_id)) as conn:
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
    if not os.path.exists(hash_path(showID=show_id)):
        raise ValueError("No such show ID.")

    with sqlite3.connect(hash_path(showID=show_id)) as conn:
        cursor = conn.cursor()
        check = cursor.execute('SELECT 1 FROM Tickets WHERE Row = ? AND Column = ? AND Place = ?',
                               (seat.row, seat.column, seat.place)).fetchone()

        if check is None:
            return True
        return False


def get_info_by_hash(show_id, ticket_hash):
    if not os.path.exists(hash_path(showID=show_id)):
        raise ValueError("No such show ID.")

    with sqlite3.connect(hash_path(showID=show_id)) as conn:
        cursor = conn.cursor()
        ticket_info = cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE Hash = ?''', (ticket_hash,)).fetchone()

        if ticket_info is None:
            return "404 no such hash."

        return ticket_info


def get_info_by_somthing(show_id, something):
    if not os.path.exists(hash_path(showID=show_id)):
        raise ValueError("No such show ID.")

    ticket_info = []
    with sqlite3.connect(hash_path(showID=show_id)) as conn:
        cursor = conn.cursor()
        try:
            ticket_info += cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                            FROM Tickets WHERE OrderNumber = ? OR TicketNumber = ? OR Hash = ? ''', (something, something, something)).fetchone()
        except:
            pass



    with sqlite3.connect(order_path(showID=show_id)) as conn:
        cursor = conn.cursor()
        try:
            ticket_info += cursor.execute('''SELECT OrderNumber, Name, Email, PhoneNumber
                                            FROM Orders WHERE OrderNumber = ? OR Name = ? OR Email = ? OR PhoneNumber = ? ''', (something, something, something, something)).fetchone()
        except:
            pass
    if ticket_info is None:
        return f"404 no such {something}."

    return ticket_info


def get_info_by_ticket_number(show_id, ticket_num):
    if not os.path.exists(hash_path(showID=show_id)):
        raise ValueError("No such show ID.")

    with sqlite3.connect(hash_path(showID=show_id)) as conn:
        cursor = conn.cursor()
        ticket_info = cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE TicketNumber = ?''', (ticket_num,)).fetchone()

        if ticket_info is None:
            return "404 no such ticket number."

        return ticket_info


def create_tickets(show_id, seats, phone_number, email, name=None):
    for seat in seats:
        if not check_seat(show_id=show_id, seat=seat):
            raise ValueError(f"Seat is taken. {seat.place}:{seat.row},{seat.column}")
    tickets = TicketGroup(show_id=show_id, seats=seats, phone_number=phone_number, email=email, name=name)
    return tickets.get_tickets()



def create_show(show_id):
    try:
        os.mkdir(folder_path(showID=show_id))
    except FileExistsError:
        pass

    with open(order_path(showID=show_id), 'w') as f:
        with sqlite3.connect(order_path(showID=show_id)) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
                            "OrderNumber" INTEGER NOT NULL,
                            "Name" TEXT,
                            "Email" TEXT NOT NULL,
                            "PhoneNumber" TEXT NOT NULL
                              )''')

    with open(hash_path(showID=show_id), 'w') as f:
        with sqlite3.connect(hash_path(showID=show_id)) as conn:
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


print(get_info_by_somthing(2,"אורי רוטר"))