from TicketGroup import *
from database_control import check_seat, folder_path, order_path, hash_path


def create_tickets(show_id, seats, phone_number, email, name=None):
    # Check if seats are available
    for seat in seats:
        if not check_seat(show_id=show_id, seat=seat):
            raise ValueError(f"Seat is taken. {seat.place}:{seat.row},{seat.column}")

    # Create TicketGroup
    tickets = TicketGroup(show_id=show_id, seats=seats, phone_number=phone_number, email=email, name=name)
    return get_tickets(tickets)


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
