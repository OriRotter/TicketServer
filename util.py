import os
import sqlite3
import shutil
import json
from cryptography.fernet import Fernet

from TicketGroup import TicketGroup
from DB_CON import DB_CON
from Strings import KEY, folder_path, shows_path, details_path, hash_path, \
    hash_encrypt_path, order_path, order_encrypt_path


def create_tickets(show_id, seats, phone_number, email, name=None):
    try:
        db = DB_CON(show_id=show_id)
        for seat in seats:
            if not db.check_seat(seat=seat):
                raise ValueError(f"Seat {seat.row},{seat.column} is already taken.")

        tickets = TicketGroup(show_id=show_id, seats=seats, phone_number=phone_number, email=email, name=name)
        info = db.get_info_tickets(tickets)
        db.close_db()
        return info
    except Exception as e:
        print(f"Error creating tickets: {e}")
        raise


def update_seat_map(show_id, seats):
    try:
        with open(f"Databases/{show_id}/seatMap.txt", 'r') as f:
            data = f.readlines()
        for seat in seats:
            data[seat.row-1] = data[seat.row-1].replace('\n','').split(',')
            data[seat.row-1][seat.column-1] = 0
            data[seat.row-1] = ','.join(str(e) for e in data[seat.row-1])
            data[seat.row-1] += "\n"
        with open(f"Databases/{show_id}/seatMap.txt", 'w') as f:
            f.write(''.join(str(e) for e in data))
    except Exception as e:
        print(f"Error updating seat map: {e}")
        raise


def get_seat_map(show_id):
    try:
        with open(f"Databases/{show_id}/seatMap.txt", 'r') as f:
            seat_map = f.readlines()
        processed_seat_map = []
        for row_index, row in enumerate(seat_map):
            row = row.strip().split(',')
            processed_row = [
                {'status': 'seat' if seat == '1' else 'seat sold' if seat == '0' else 'space',
                 'index': f"{row_index + 1},{seat_index + 1}" if seat == '0' or seat == '1' else None} for
                seat_index, seat in enumerate(row)]
            processed_seat_map.append(processed_row)
        return processed_seat_map
    except Exception as e:
        print(f"Error getting seat map: {e}")
        raise


def create_seat_map(show_id, seat_map):
    try:
        with open(f"Databases/{show_id}/seatMap.txt", 'w') as f:
            data = ""
            for line in seat_map:
                data += ",".join(str(seat) for seat in line)
                data += "\n"
            f.write(data)
    except Exception as e:
        print(f"Error creating seat map: {e}")
        raise


def create_show(show_id, name, price, seat_map, img):
    try:
        if show_id in get_shows_values():
            raise ValueError("Show code is already taken.")

        os.makedirs(folder_path(showID=show_id), exist_ok=True)

        with sqlite3.connect(order_path(showID=show_id)) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
                            "OrderNumber" INTEGER PRIMARY KEY,
                            "Name" TEXT,
                            "Email" TEXT NOT NULL,
                            "PhoneNumber" TEXT NOT NULL
                              )''')

        with sqlite3.connect(hash_path(showID=show_id)) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS Tickets (
                            "OrderNumber" INTEGER,
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
        create_seat_map(show_id, seat_map)

        show_info = {"name": name, "price": price, "show_id": show_id, "img": img}
        with open(details_path(showID=show_id), 'w') as fp:
            json.dump(show_info, fp)

        with open(shows_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = {}
        data[name] = show_id
        with open(shows_path, 'w') as f:
            json.dump(data,f)

    except Exception as e:
        print(f"Error creating show: {e}")
        raise


def del_show_by_show_id(show_id):
    try:
        img = get_show_details(show_id)["img"]
        os.remove(f"templates/uploads/{img}")
        shutil.rmtree(folder_path(show_id))

        with open(shows_path, 'r') as f:
            data = json.load(f)

        items = list(data.keys())
        for item in items:
            if int(show_id) == int(data[item]):
                with open(shows_path, 'w') as f:
                    data.pop(item)
                    json.dump(data, f)
    except Exception as e:
        print(f"Error deleting show: {e}")
        raise


def get_show_details(show_id):
    try:
        with open(details_path(show_id), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error getting show details: {e}")
        raise


def get_shows_name():
    try:
        with open(shows_path, 'r') as f:
            shows = json.load(f)
        return list(shows.keys())
    except Exception as e:
        print(f"Error getting show names: {e}")
        raise


def get_shows_values():
    try:
        with open(shows_path, 'r') as f:
            shows = json.load(f)
        return list(shows.values())
    except Exception as e:
        print(f"Error getting show values: {e}")
        return []
