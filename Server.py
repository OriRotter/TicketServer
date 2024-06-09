import json

from flask import Flask, render_template, request, send_file, session, redirect, url_for
import hashlib
from DB_CON import DB_CON
from Seat import Seat
from Strings import KEY, admin_username, admin_password
from util import create_tickets, get_seat_map, update_seat_map, create_show, get_shows_name, get_shows_values, \
    get_show_details, del_show_by_show_id

app = Flask(__name__)
app.secret_key = KEY

@app.route("/")
def home():
    show_data = [get_show_details(id) for id in get_shows_values()]
    return render_template("home.html", data=show_data)


@app.route('/buy', methods=["GET"])
def redirect_to_home():
    return redirect("/")


@app.route('/buy', methods=["POST"])
def buy():
    try:
        show_id = int(request.form['show_id'].strip())
        data = get_show_details(show_id)
        return render_template("buy.html", seat_map=get_seat_map(show_id), show_detail=data)
    except Exception as e:
        app.logger.error("An error occurred during user move to buy: %s", e)
        return render_template("error.html", error_message=f"An error occurred during moving to buy. {e}")


@app.route('/order', methods=["POST"])
def order_handle():
    try:
        show_id = int(request.form['showID'].strip())
        email = request.form['email'].strip()
        phone_number = request.form['phoneNumber'].strip()
        name = request.form['name'].strip()
        seats_user = [Seat(*map(int, seat.split(','))) for seat in request.form['seats'].split('.')]

        db = DB_CON(show_id)
        order_info = [db.get_order_number(), name, email, phone_number]
        db.close_db()

        tickets_info = create_tickets(show_id=show_id, email=email, phone_number=phone_number, name=name,
                                      seats=seats_user)
        update_seat_map(show_id, seats_user)

        ticket_url = f"{request.url.replace('/order', '')}/showTicket?showID={show_id}&hash={list(tickets_info.keys())[0]}"

        return render_template("tickets.html", tickets_info=tickets_info, order_info=order_info, ticket_url=ticket_url)

    except Exception as e:
        app.logger.error("An error occurred during ticket creation: %s", e)
        return render_template("error.html", error_message=f"An error occurred during ticket creation. {e}")


@app.route('/images/<img_name>.png', methods=["GET"])
def get_image(img_name):
    return send_file(f"templates/images/{img_name}.png", mimetype="image/gif")


@app.route('/static/uploads/<img_name>.<img_type>', methods=["GET"])
def get_image_uploads(img_name, img_type):
    return send_file(f"templates/uploads/{img_name}.{img_type}", mimetype="image/gif")


@app.route('/showTicket', methods=["GET"])
def show_ticket():
    try:
        show_id = int(request.args.get('showID').strip())
        ticket_hash = request.args.get('hash').strip()

        db = DB_CON(show_id=show_id)
        ticket_order_number = db.get_info_by_hash(ticket_hash)[0]
        order_info = db.get_info_by_orderNumber_order(ticket_order_number)
        ticket_details = db.get_info_by_orderNumber_ticket(ticket_order_number)
        db.close_db()

        ticket_info = {ticket[5]: [ticket[0], ticket[1], ticket[2], ticket[3], bool(ticket[4])] for ticket in
                       ticket_details}

        return render_template("tickets.html", tickets_info=ticket_info, order_info=order_info, ticket_url=request.url)

    except ValueError as ve:
        app.logger.error("Invalid input format: %s", ve)
        return render_template("error.html", error_message=f"Invalid input format. {ve}")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = hashlib.sha256(request.form['username'].strip().encode()).hexdigest()
    password = hashlib.sha256(request.form['password'].strip().encode()).hexdigest()

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
        if session.get('username') == admin_username and session.get('password') == admin_password:
            if request.method == "POST":
                show_id = int(request.form['showID'].strip())
                name = request.form['name'].strip()
                price = int(request.form['price'].strip())
                seat_map = json.loads(request.form['seatMap'])
                img_file = request.files['img']

                create_show(show_id=show_id, name=name, price=price, seat_map=seat_map, img=img_file.filename)
                img_file.save("templates/uploads/" + img_file.filename)

                return render_template("success.html", success_message="The show successfully created.")

            if request.method == "GET":
                return render_template("create_show.html")

        return redirect(url_for('login'))

    except Exception as e:
        app.logger.error("An error occurred during show create: %s", e)
        return render_template("error.html", error_message=f"An error occurred during show create. {e}")


@app.route('/del_show', methods=["GET", "POST"])
def del_show():
    if session.get('username') == admin_username and session.get('password') == admin_password:
        if request.method == "GET":
            show_data = [get_show_details(id) for id in get_shows_values()]
            return render_template("del_show.html", data=show_data)

        if request.method == "POST":
            show_id = request.form["show_id"].strip()
            del_show_by_show_id(show_id)
            return render_template("success.html", success_message="The show successfully deleted.")


#APP

@app.route('/get_shows', methods=["GET"])
def get_shows():
    return json.dumps(get_shows_name())


@app.route('/get_shows_id', methods=["GET"])
def get_shows_id():
    return json.dumps(get_shows_values())


@app.route('/use', methods=["POST"])
def use():
    password = request.form['password'].strip()
    if hashlib.sha256(password.encode()).hexdigest() != admin_password:
        return
    ticket_hash = request.form['hash'].strip()
    show_id = int(request.form['showID'].strip())

    db = DB_CON(show_id=show_id)
    result = db.use_hash(ticket_hash=ticket_hash)
    db.close_db()

    return str(result)

@app.route('/change', methods=["POST"])
def change():
    password = request.form['password'].strip()
    if hashlib.sha256(password.encode()).hexdigest() != admin_password:
        return
    ticket_hash = request.form['hash'].strip()
    show_id = int(request.form['showID'].strip())

    db = DB_CON(show_id=show_id)
    result = db.change_use(ticket_hash=ticket_hash)
    db.close_db()

    return str(result)

@app.route('/search', methods=["POST"])
def search():
    try:
        password = request.form['password'].strip()
        if hashlib.sha256(password.encode()).hexdigest() != admin_password:
            return
        text = request.form['search'].strip()
        show_id = int(request.form['showID'].strip())
        db = DB_CON(show_id=show_id)
        result = db.get_info_by_something(something=text)
        db.close_db()

        return json.dumps(result)

    except:

        result = [[],[]]
        return json.dumps(result)

@app.route('/order_number', methods=["POST"])
def order_number():
    try:
        password = request.form['password'].strip()
        if hashlib.sha256(password.encode()).hexdigest() != admin_password:
            return
        order_number_user = request.form['order_number'].strip()
        show_id = int(request.form['showID'].strip())
        db = DB_CON(show_id=show_id)
        result = db.get_info_by_orderNumber_ticket(order_number=order_number_user)
        db.close_db()

        return json.dumps(result)

    except:

        result = []
        return json.dumps(result)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

