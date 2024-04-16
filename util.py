from TicketGroup import *
from DB_CON import DB_CON
from Strings import *
import sqlite3
import os
from cryptography.fernet import Fernet


def create_tickets(show_id, seats, phone_number, email, name=None):
    # Check if seats are available
    db = DB_CON(show_id=show_id)
    for seat in seats:
        if not db.check_seat(seat=seat):
            raise ValueError(f"Seat is taken. {seat.place}:{seat.row},{seat.column}")

    # Create TicketGroup
    tickets = TicketGroup(show_id=show_id, seats=seats, phone_number=phone_number, email=email, name=name)
    info = db.get_info_tickets(tickets)
    db.close_db()
    return info


def create_show(show_id):
    # Create directory for the show if it doesn't exist
    try:
        os.makedirs(folder_path(showID=show_id), exist_ok=True)
    except OSError as e:
        print(f"Error creating directory for show {show_id}: {e}")

    # Create or connect to Orders database
    with sqlite3.connect(order_path(showID=show_id)) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
                        "OrderNumber" INTEGER PRIMARY KEY,
                        "Name" TEXT,
                        "Email" TEXT NOT NULL,
                        "PhoneNumber" TEXT NOT NULL
                          )''')

    # Create or connect to Tickets database
    with sqlite3.connect(hash_path(showID=show_id)) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Tickets (
                        "OrderNumber" INTEGER,
                        "Place" TEXT,
                        "Row" INTEGER,
                        "Column" INTEGER,
                        "TicketNumber" INTEGER NOT NULL PRIMARY KEY,
                        "Used" BOOLEAN NOT NULL,
                        "Hash" TEXT NOT NULL
                          )''')
    cursor.close()
    conn.close()
    hashDB = hash_path(show_id)
    hashDB_encrypt = hash_encrypt_path(show_id)
    orderDB = order_path(show_id)
    orderDB_encrypt = order_encrypt_path(show_id)
    f = Fernet(KEY)
    with open(hashDB, "rb") as file:
        file_data = file.read()
    file.close()
    encrypted_data = f.encrypt(file_data)
    with open(hashDB_encrypt, "wb") as file:
        file.write(encrypted_data)
    with open(orderDB, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(orderDB_encrypt, "wb") as file:
        file.write(encrypted_data)

    os.remove(hashDB)
    os.remove(orderDB)
