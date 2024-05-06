# Import necessary modules and classes
import json
from flask import Flask, render_template, request, send_file, session, redirect, url_for
import shutil
from util import create_tickets, getSeatMap, updateSeatMap, create_show, get_shows_name, get_shows_values, get_show_details
from Seat import Seat
from DB_CON import DB_CON
import os
from Strings import KEY, admin_password, admin_username, folder_path, shows_path

# Initialize Flask application
app = Flask(__name__)


# Define route handlers
@app.route("/")
def home():
    show_data = []
    ids = get_shows_values()
    for id in ids:
        show_data.append(get_show_details(id))
    return render_template("home.html", data=show_data)


@app.route('/buy', methods=["GET"])
def redirect_to_home():
    return redirect("/")

@app.route('/buy', methods=["POST"])
def buy():
    try:
        show_id = int(request.form['show_id'].strip())
        data = get_show_details(show_id)
        return render_template("buy.html", seatMap=getSeatMap(show_id),show_detail=data)
    except Exception as e:
        app.logger.error("An error occurred during user move to buy: %s", e)
        return render_template("error.html", error_message=f"An error occurred during moving to buy. {e}")

@app.route('/order', methods=["POST"])
def order_handle():
    try:
        # Sanitize user inputs
        show_id = int(request.form['showID'].strip())
        email = request.form['email'].strip()
        phone_number = request.form['phoneNumber'].strip()
        name = request.form['name'].strip()
        seatsUser = request.form['seats'].split('.')
        seats = []
        for seat in seatsUser:
            seat = seat.split(',')
            seats.append(Seat(row=int(seat[0]), column=int(seat[1])))
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
        ticket_url = f"{request.url.replace('/order','')}/showTicket?showID={show_id}&hash={list(tickets_info.keys())[0]}"
        # Render tickets page
        return render_template("tickets.html", tickets_info=tickets_info, order_info=order_info,ticket_url=ticket_url)

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
        return f"{result}"

    except ValueError as ve:
        app.logger.error("Invalid input format: %s", ve)
        return render_template("error.html", error_message=f"Invalid input format. {ve}")

    except Exception as e:
        app.logger.error("An error occurred during ticket usage: %s", e)
        return render_template("error.html", error_message=f"An error occurred during ticket usage. {e}")


@app.route('/images/<img_name>.png', methods=["GET"])
def get_image(img_name):
    return send_file(f"templates/images/{img_name}.png", mimetype="image/gif")

@app.route('/static/uploads/<img_name>.<img_type>', methods=["GET"])
def get_image_uploads(img_name,img_type):
    return send_file(f"templates/uploads/{img_name}.{img_type}", mimetype="image/gif")
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
            ticket_info[f"{ticket[5]}"] = [
                ticket[0], ticket[1], ticket[2], ticket[3], bool(ticket[4])]
        return render_template("tickets.html", tickets_info=ticket_info, order_info=order_info,ticket_url=request.url)

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
    try:
        if session.get('username') == admin_username and session.get('password'):
            if request.method == "POST":
                show_id = int(request.form['showID'].strip())
                name = request.form['name'].strip()
                price = int(request.form['price'].strip())
                seatMap = json.loads(request.form['seatMap'])
                img_file = request.files['img']
                create_show(show_id=show_id,name=name,price=price, seat_map=seatMap,img=img_file.filename)
                img_file.save("templates/uploads/" + img_file.filename)
                return render_template("success.html",success_message="The show successfully created.")
            if request.method == "GET":
                return render_template("create_show.html")
        return redirect(url_for('login'))
    except Exception as e:
        app.logger.error("An error occurred during show create: %s", e)
        return render_template("error.html", error_message=f"An error occurred during show create. {e}")


@app.route('/search', methods=["POST"])
def search():
    try:
        show_id = int(request.args.get('showID').strip())
        text = request.args.get('search').strip()
        db = DB_CON(show_id=show_id)
        r = db.get_info_by_something(something=text)
        db.close_db()
        return json.dump(r)
    except:
        db = DB_CON(show_id=1)
        r = db.get_info_by_something(something="1")
        db.close_db()
        return json.dumps(r)
@app.route('/get_shows', methods=["GET"])
def get_shows():
    return f"{json.dumps(get_shows_name())}"

@app.route('/get_shows_id', methods=["GET"])
def get_shows_id():
    return f"{json.dumps(get_shows_values())}"


@app.route('/del_show', methods=["GET","POST"])
def del_show():
    if session.get('username') == admin_username and session.get('password'):
        if request.method == "GET":
            show_data = []
            ids = get_shows_values()
            for id in ids:
                show_data.append(get_show_details(id))
            return render_template("del_show.html", data=show_data)
        if request.method == "POST":
            show_id = request.form["show_id"].strip()
            shutil.rmtree(folder_path(show_id))
            with open(shows_path, 'r') as f:
                data = json.load(f)

            items = list(data.keys())
            for item in items:
                if int(show_id) == int(data[item]):
                    with open(shows_path, 'w') as f:
                        data.pop(item)
                        json.dump(data,f)
                    return render_template("success.html", success_message="The show successfully deleted.")

# Run the Flask application
if __name__ == '__main__':
    port = int(os.getenv('PORT', 25565))
    app.secret_key = KEY
    app.run(host='192.168.150.13', port=port)
