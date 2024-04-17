from flask import Flask, render_template, request
from util import create_tickets
from Seat import Seat
from DB_CON import DB_CON
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/buy", methods=["GET"])
def buy():
    return render_template("buy.html")


@app.route('/buy', methods=["POST"])
def show_tickets():
    try:
        # Sanitize user inputs
        show_id = int(request.form['showID'].strip())
        email = request.form['email'].strip()
        phone_number = request.form['phoneNumber'].strip()
        name = request.form['name'].strip()
        place = request.form['place'].strip()
        rows = list(map(int, request.form['row'].strip().split(',')))
        columns = list(map(int, request.form['column'].strip().split(',')))

        seats = [Seat(place=place, row=row, column=column) for row, column in zip(rows, columns)]

        # Create tickets and generate QR codes
        tickets_info = create_tickets(
            show_id=show_id,
            email=email,
            phone_number=phone_number,
            name=name,
            seats=seats
        )

        return render_template("tickets.html", tickets_info=tickets_info)

    except ValueError as ve:
        app.logger.error("Invalid input format: %s", ve)
        return render_template("error.html", error_message=f"Invalid input format. {ve}")

    except Exception as e:
        app.logger.error("An error occurred during ticket creation: %s", e)
        return render_template("error.html", error_message=f"An error occurred during ticket creation. {e}")


@app.route('/use', methods=["POST"])
def use():
    try:
        # Sanitize user inputs
        ticket_hash = request.form['hash'].strip()
        show_id = int(request.form['showID'].strip())

        # Use ticket
        db = DB_CON(show_id=show_id)
        result = db.use_hash(ticket_hash=ticket_hash)
        return f"<h1>{result}<h1>"

    except ValueError as ve:
        app.logger.error("Invalid input format: %s", ve)
        return render_template("error.html", error_message=f"Invalid input format. {ve}")

    except Exception as e:
        app.logger.error("An error occurred during ticket usage: %s", e)
        return render_template("error.html", error_message=f"An error occurred during ticket usage. {e}")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 25565))
    app.run(host='0.0.0.0', port=port)
