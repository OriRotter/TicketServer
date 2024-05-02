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


def updateSeatMap(show_id, seats):
    try:
        with open(f"Databases/{show_id}/seatMap.txt", 'r') as f:
            data = f.readlines()
        for seat in seats:
            data[seat.row-1] = data[seat.row-1].replace('\n','').split(',')
            data[seat.row-1][seat.column-1] = 1
            data[seat.row-1] = ','.join(str(e) for e in data[seat.row-1])
            data[seat.row-1] += "\n"
        with open(f"Databases/{show_id}/seatMap.txt", 'w') as f:
            f.write(''.join(str(e) for e in data))
    except:
        return
def getSeatMap(show_id):
    try:
        with open(f"Databases/{show_id}/seatMap.txt", 'r') as f:
            seat_map = f.readlines()
        processed_seat_map = []
        for row_index, row in enumerate(seat_map):
            row = row.strip().split(',')
            processed_row = [
                {'status': 'seat' if seat == '0' else 'seat sold' if seat == '1' else 'space',
                 'index': f"{row_index + 1},{seat_index + 1}" if seat == '0' or seat == '1' else None} for
                seat_index, seat in enumerate(row)]
            processed_seat_map.append(processed_row)
        return processed_seat_map
    except:
        with open(f"Databases/seatMap.txt", 'r') as f:
            seat_map = f.readlines()
        processed_seat_map = []
        for row_index, row in enumerate(seat_map):
            row = row.strip().split(',')
            processed_row = [
                {'status': 'seat' if seat == '0' else 'seat sold' if seat == '1' else 'space',
                 'index': f"{row_index + 1},{seat_index + 1}"} for seat_index, seat in enumerate(row)]
            processed_seat_map.append(processed_row)
        return processed_seat_map

def createSeatMap(show_id, seat_map):
    try:
        with open(f"Databases/{show_id}/seatMap.txt", 'w') as f:
            data = ""
            for line in seat_map:
                data += ",".join(str(seat) for seat in line)
                data += "\n"
            f.write(data)
    except:
        raise ValueError("Can not create seat map.")


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