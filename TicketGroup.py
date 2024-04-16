from DB_CON import DB_CON
from Ticket import Ticket
import re

class TicketGroup:
    def __init__(self, show_id, seats, phone_number, email, name=None):
        self._show_id = show_id
        self._name = name
        self._validate_phone_number(phone_number)
        self._phone_number = phone_number
        self._validate_email(email)
        self._email = email

        db = DB_CON(show_id=show_id)

        self._order_number = db.get_order_number()
        self._tickets = []
        self._ticket_number = db.get_order_number()

        for seat in seats:
            ticket = Ticket(self._order_number, self._show_id, self._ticket_number, seat)
            self._tickets.append(ticket)
            self._ticket_number += 1

        db.store_order(ticketGroup=self)
        self._store_hashes(db)
        db.close_db()



    def _store_hashes(self, db):
        for ticket in self._tickets:
            db.store_ticket(ticket)

    def _validate_phone_number(self, phone_number):
        if not re.match(r'^05\d{8}$', phone_number):
            raise ValueError("Invalid phone number")

    def _validate_email(self, email):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email")

    @property
    def show_id(self):
        return self._show_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if '@' not in email:
            raise ValueError("Invalid email")
        self._email = email

    @property
    def order_number(self):
        return self._order_number

    @order_number.setter
    def order_number(self, order_number):
        self._order_number = order_number

    @property
    def tickets(self):
        return self._tickets

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self,phone_number):
        self._phone_number = phone_number