# Import necessary modules and classes
import json
from flask import Flask, render_template, request, send_file, session, redirect, url_for
from util import create_tickets, getSeatMap, updateSeatMap, create_show, createSeatMap
from Seat import Seat
from DB_CON import DB_CON
import os
from Strings import KEY, admin_password, admin_username

# Initialize Flask application
app = Flask(__name__)


# Define route handlers
@app.route("/")
def home():
    return render_template("home.html")


@app.route('/buy', methods=["GET"])
def buy():
    return render_template("buy.html", seatMap=getSeatMap(1))


@app.route('/buy', methods=["POST"])
def show_tickets():
    try:
        # Sanitize user inputs
        show_id = int(request.form['showID'].strip())
        email = request.form['email'].strip()
        phone_number = request.form['phoneNumber'].strip()
        name = request.form['name'].strip()
        place = request.form['place'].strip()
        seatsUser = request.form['seats'].split('.')
        seats = []
        for seat in seatsUser:
            seat = seat.split(',')
            seats.append(Seat(place=place, row=int(seat[0]), column=int(seat[1])))
        db = DB_CON(show_id)
        order_info = [db.get_order_number(), name, email, phone_number]
        db.close_db()
        # Create tickets and update seat map
        tickets_info = create_tickets(
            show_id=show_id,
            email=email,
            phone_number=phone_number,
            name=name,
            seats=seats
        )
        updateSeatMap(show_id, seats)
        # Render tickets page
        return render_template("tickets.html", tickets_info=tickets_info, order_info=order_info)

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
        db.close_db()
        return f"<h1>{result}<h1>"

    except ValueError as ve:
        app.logger.error("Invalid input format: %s", ve)
        return render_template("error.html", error_message=f"Invalid input format. {ve}")

    except Exception as e:
        app.logger.error("An error occurred during ticket usage: %s", e)
        return render_template("error.html", error_message=f"An error occurred during ticket usage. {e}")


@app.route('/images/<img_name>.png', methods=["GET"])
def get_image(img_name):
    return send_file(f"templates/images/{img_name}.png", mimetype="image/gif")


@app.route('/showTicket', methods=["GET"])
def showTicket():
    try:
        show_id = int(request.args.get('showID').strip())
        hash = request.args.get('hash').strip()
        db = DB_CON(show_id=show_id)
        ticket_order_number = db.get_info_by_hash(hash)[0]
        ticket_details = db.get_info_by_orderNumber_ticket(ticket_order_number)
        order_info = db.get_info_by_orderNumber_order(ticket_order_number)
        db.close_db()
        ticket_info = {}
        for ticket in ticket_details:
            ticket_info[f"{ticket[6]},{ticket_order_number}"] = [
                ticket[0], ticket[1], ticket[2], ticket[3], ticket[4], bool(ticket[5])]

        return render_template("tickets.html", tickets_info=ticket_info, order_info=order_info)

    except ValueError as ve:
        app.logger.error("Invalid input format: %s", ve)
        return render_template("error.html", error_message=f"Invalid input format. {ve}")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    if username == admin_username and password == admin_password:
        session['username'] = username
        session['password'] = password
        return redirect(url_for('admin'))
    else:
        return render_template("login.html")


@app.route('/admin', methods=["GET", "POST"])
def admin():
    if session.get('username') == admin_username and session.get('password') == admin_password:
        return render_template("admin_panel.html")
    return redirect(url_for('login'))


@app.route('/create_show', methods=["GET", "POST"])
def create_show_page():
    if session.get('username') == admin_username and session.get('password'):
        show_id = int(request.form['showID'].strip())
        name = request.form['name'].strip()
        price = int(request.form['price'].strip())
        seatMap = json.loads(request.form['seatMap'])
        create_show(show_id)
        createSeatMap(show_id=show_id, seat_map=seatMap)
        return render_template("success.html",success_message="The show successfully created.")
    return redirect(url_for('login'))



@app.route('/get_shows', methods=["GET"])
def get_shows():
    a = ['1','2','3']
    return f"{json.dumps(a)}"

@app.route('/get_shows_id', methods=["GET"])
def get_shows_id():
    a = ['1','2','3']
    return f"{json.dumps(a)}"

@app.route('/test', methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return render_template("test.html")
    print(request.form)
    row = request.form['row']
    print(row)
    return render_template("error.html")


# Run the Flask application
if __name__ == '__main__':
    port = int(os.getenv('PORT', 25565))
    app.secret_key = KEY
    app.run(host='127.0.0.1', port=port)
