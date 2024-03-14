from flask import Flask, render_template, request
from util import *
from Classes import Seat

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
        show_id = request.form['showID'].strip()
        email = request.form['email'].strip()
        phone_number = request.form['phoneNumber'].strip()
        name = request.form['name'].strip()
        place = request.form['place'].strip()
        row = request.form['row'].strip()
        column = request.form['column'].strip()

        # Create tickets and generate QR codes
        tickets_info = create_tickets(
            show_id=int(show_id),
            email=email,
            phone_number=phone_number,
            name=name,
            seats=[Seat(place=place, row=int(row), column=int(column))]
        )
        print(tickets_info)

        return render_template("tickets.html", tickets_info=tickets_info)

    except Exception as e:
        app.logger.error("An error occurred during ticket creation: %s", e)
        return render_template("error.html", error_message=f"An error occurred during ticket creation. {e}")


@app.route('/use', methods=["GET"])
def use():
    return render_template("use.html")


@app.route('/use', methods=["POST"])
def used():
    try:
        # Sanitize user inputs
        ticket_hash = request.form['hash'].strip()
        show_id = request.form['showID'].strip()

        # Use ticket
        result = use_hash(ticket_hash=ticket_hash, show_id=show_id)
        return f"<h1>{result}<h1>"

    except Exception as e:
        app.logger.error("An error occurred during ticket usage: %s", e)
        return render_template("error.html", error_message=f"An error occurred during ticket usage. {e}")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 25565))
    app.run(host='0.0.0.0', port=port)
