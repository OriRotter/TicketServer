from database_control import *
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
        self._order_number = get_order_number(self)
        self._tickets = []
        self._ticket_number = get_order_number(self)

        for seat in seats:
            ticket = Ticket(self._order_number, self._show_id, self._ticket_number, seat)
            self._tickets.append(ticket)
            self._ticket_number += 1

        store_order(ticketGroup=self)
        store_hashes(ticketGroup=self)

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