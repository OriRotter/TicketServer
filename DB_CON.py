import sqlite3

from Strings import *
from cryptography.fernet import Fernet


class DB_CON:
    def __init__(self, show_id):
        self._show_id = show_id
        hashDB = hash_encrypt_path(showID=show_id)
        orderDB = order_encrypt_path(showID=show_id)

        if self._fileValid(hashDB) and self._fileValid(orderDB):
            self._decrypt_db(KEY)
        hashDB = hash_path(show_id)
        orderDB = order_path(show_id)
        if not self._fileValid(hashDB) and not self._fileValid(orderDB):
            raise ValueError("No such show.")
        self._order_conn = sqlite3.connect(orderDB)
        self._hash_conn = sqlite3.connect(hashDB)
        self._order_cursor = self._order_conn.cursor()
        self._hash_cursor = self._hash_conn.cursor()

    def _fileValid(self, path):
        if not os.path.exists(path):
            return False
        return True

    def close_db(self):
        self._hash_conn.commit()
        self._order_conn.commit()
        self._hash_cursor.close()
        self._order_cursor.close()
        self._hash_conn.close()
        self._order_conn.close()
        self._encrypt_db()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._hash_conn.commit()
        self._order_conn.commit()
        self._hash_cursor.close()
        self._order_cursor.close()
        self._hash_conn.close()
        self._order_conn.close()
        self._encrypt_db()

    def _encrypt_db(self, KEY=KEY):
        try:
            hashDB = hash_path(self._show_id)
            hashDB_encrypt = hash_encrypt_path(self._show_id)
            orderDB = order_path(self._show_id)
            orderDB_encrypt = order_encrypt_path(self._show_id)
            f = Fernet(KEY)
            with open(hashDB, "rb") as file:
                file_data = file.read()
            os.remove(hashDB)
            encrypted_data = f.encrypt(file_data)
            with open(hashDB_encrypt, "wb") as file:
                file.write(encrypted_data)

            with open(orderDB, "rb") as file:
                file_data = file.read()
            os.remove(orderDB)
            encrypted_data = f.encrypt(file_data)
            with open(orderDB_encrypt, "wb") as file:
                file.write(encrypted_data)
        except:
            return

    def _decrypt_db(self, KEY=KEY):
        try:
            hashDB = hash_path(self._show_id)
            hashDB_encrypt = hash_encrypt_path(self._show_id)
            orderDB = order_path(self._show_id)
            orderDB_encrypt = order_encrypt_path(self._show_id)
            f = Fernet(KEY)
            with open(hashDB_encrypt, "rb") as file:
                encrypted_data = file.read()
            os.remove(hashDB_encrypt)
            decrypted_data = f.decrypt(encrypted_data)
            with open(hashDB, "wb") as file:
                file.write(decrypted_data)

            with open(orderDB_encrypt, "rb") as file:
                encrypted_data = file.read()
            os.remove(orderDB_encrypt)

            decrypted_data = f.decrypt(encrypted_data)
            with open(orderDB, "wb") as file:
                file.write(decrypted_data)
        except:
            return

    def use_hash(self, ticket_hash):
        used = self._hash_cursor.execute('SELECT Used FROM Tickets WHERE Hash = ?', (ticket_hash,)).fetchone()

        if used is None:
            return "404 no such hash."

        if not used[0]:
            self._hash_cursor.execute('UPDATE Tickets SET Used = 1 WHERE Hash = ?', (ticket_hash,))
            self._hash_conn.commit()
            return "200 OK"

        return "300 Hash used."

    def check_seat(self, seat):
        check = self._hash_cursor.execute('SELECT 1 FROM Tickets WHERE Row = ? AND Column = ? AND Place = ?',
                                          (seat.row, seat.column, seat.place)).fetchone()

        return check is None

    def get_info_by_hash(self, ticket_hash):
        ticket_info = self._hash_cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE Hash = ?''', (ticket_hash,)).fetchone()

        return ticket_info or "404 no such hash."

    def get_info_by_something(self, something):
        ticket_info = []
        try:
            ticket_info += self._hash_cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                            FROM Tickets WHERE OrderNumber = ? OR TicketNumber = ? OR Hash = ? ''',
                                                     (something, something, something)).fetchall()
            ticket_info += self._order_cursor.execute('''SELECT OrderNumber, Name, Email, PhoneNumber
                                            FROM Orders WHERE OrderNumber = ? OR Name = ? OR Email = ? OR PhoneNumber = ? ''',
                                                      (something, something, something, something)).fetchall()
        except sqlite3.Error:
            pass

        return ticket_info or f"404 no such {something}."

    def get_info_by_orderNumber_ticket(self, order_number):
        ticket_info = self._hash_cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used, Hash
                                            FROM Tickets WHERE OrderNumber = ?''',
                                                     (order_number,)).fetchall()

        return ticket_info or f"404 no such {order_number}."

    def get_info_by_orderNumber_order(self, order_number):
        order_info = self._order_cursor.execute('''SELECT OrderNumber, Name, Email, PhoneNumber
                                            FROM Orders WHERE OrderNumber = ?''',
                                                     (order_number,)).fetchone()

        return order_info or f"404 no such {order_number}."
    def get_info_by_ticket_number(self, ticket_num):
        ticket_info = self._hash_cursor.execute('''SELECT OrderNumber, Place, Row, Column, TicketNumber, Used
                                        FROM Tickets WHERE TicketNumber = ?''', (ticket_num,)).fetchone()

        return ticket_info or "404 no such ticket number."

    def store_ticket(self, ticket):
        self._hash_cursor.execute('''INSERT INTO Tickets (OrderNumber, Place, Row, Column, TicketNumber, Used, Hash)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                  (ticket.order_number, ticket.place, ticket.row, ticket.column,
                                   ticket.ticket_num, ticket.used, ticket.hash))
        self._hash_conn.commit()

    def get_ticket_number(self):
        try:
            max_ticket_number = self._hash_cursor.execute("SELECT MAX(TicketNumber) FROM Tickets").fetchone()[0]
            return (max_ticket_number or 0) + 1
        except:
            return 1

    def get_order_number(self):

        try:
            max_order_number = self._order_cursor.execute("SELECT MAX(OrderNumber) FROM Orders").fetchone()[0]
            return (max_order_number or 0) + 1
        except:
            return 1

    def store_order(self, ticketGroup):
        self._order_cursor.execute('''INSERT INTO Orders (OrderNumber, Name, Email, PhoneNumber)
                                      VALUES (?, ?, ?, ?)''',
                                   (ticketGroup.order_number, ticketGroup.name, ticketGroup.email,
                                    ticketGroup.phone_number))
        self._order_conn.commit()

    def get_info_tickets(self, ticketGroup):
        ticket_info = {}
        for ticket in ticketGroup.tickets:
            ticket_info[f"{ticket.hash},{ticket.show_id}"] = [
                ticket.order_number, ticket.place, ticket.row, ticket.column, ticket.ticket_num, bool(ticket._used)]
        return ticket_info
