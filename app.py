from flask import *
import hashlib, sqlite3, uuid

app = Flask(__name__)

# All the HTML Templates for App Routing
template = "lfs-index.html"
loginTemplate = "login.html"
dashboardTemplate = "staff/dashboard.html"

database = "data/database.db"


# Custom Console Printing
def consolePrint(prefix, message):
    print("LFS", "|", prefix, ":", message)


@app.route("/", methods=["GET", "POST"])
def root():
    return render_template(template)


"""
@app.route("/track", methods=["POST"])
def track():
    if request.method == 'POST':
        _trackingCode = request.form['trackingCode'].encode('utf-8')
        try:
            c.execute("SELECT * FROM lfs_articles WHERE articleNumber = ?", _trackingCode)
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        _email = request.form['email']
        _password = request.form['password'].encode('utf-8')
        print(_email, _password, hashlib.sha256(_password).hexdigest())
        try:
            with sqlite3.connect('data/database.db') as lfs_db:
                c = lfs_db.cursor()
                print(c.execute("SELECT password FROM lfs_users WHERE email = ?", (_email,)).fetchone()[0])
                if c.execute("SELECT password FROM lfs_users WHERE email = ?", (_email,)).fetchone()[
                    0] == hashlib.sha256(_password).hexdigest():
                    _response = make_response(redirect(url_for('admin')))
                    _userUuid = str(uuid.uuid1())
                    # Set the Current Session the the unique userUuid
                    c.execute("UPDATE lfs_users SET currentSession = ? WHERE email = ?", (_userUuid, _email))
                    consolePrint(request.remote_addr, ("Session Created:", _userUuid))
                    # Set the Browser Cookies for userSession and username
                    _response.set_cookie('sKey', value=_userUuid)
                    return _response
                else:
                    print("Unauthenticated Access")
                    return render_template(loginTemplate)
        except (ValueError, KeyError, TypeError) as error:
            print("Error in Authenticating:", error)
            return render_template(loginTemplate)
    return render_template(loginTemplate)


@app.route("/admin")
def admin():
    # Verify User Session and Acquire additional user information through cookies
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get("sKey")
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            try:
                _alias = c.execute("SELECT name FROM lfs_users WHERE currentSession = ?", (_session,))
                _uid = c.execute("SELECT userId FROM lfs_users WHERE currentSession = ?", (_session,))
                _cc = c.execute("SELECT COUNT(*) FROM lfs_customers").fetchone()[0]
                _ec = c.execute("SELECT COUNT(*) FROM lfs_users").fetchone()[0]
                _ac = c.execute("SELECT COUNT(*) FROM lfs_articles").fetchone()[0]
            except:
                print("Unauthenticated? SQL?")
                return redirect(url_for('login'))
            print("Authenticated?")
            return render_template(dashboardTemplate, customerCount=_cc, employeeCount=_ec, articleCount=_ac)
        else:
            print("Unauthenticated?")
            return redirect(url_for('login'))


@app.route("/admin/articles")
def adminArticles():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get("sKey")
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            try:
                _a = c.execute("SELECT * FROM lfs_articles").fetchall()
                _n = c.execute("SELECT name FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()[0]
            except:
                return render_template("staff/articles.html")
            return render_template("staff/articles.html", articles=_a, name=_n)
        else:
            return redirect(url_for("login"))


@app.route("/admin/employees")
def adminEmployees():
    return render_template("staff/employees.html")


@app.route("/admin/customers")
def adminCustomers():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get("sKey")
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            try:
                _c = c.execute("SELECT * FROM lfs_customers").fetchall()
                _a = c.execute("SELECT * FROM lfs_addresses").fetchall()
                _n = c.execute("SELECT name FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()[0]
            except:
                return render_template("staff/customers.html")
            return render_template("staff/customers.html", customers=_c, addresses=_a, name=_n)
        else:
            return redirect(url_for("login"))

@app.route("/admin/articles/createarticle", methods=["POST"])
def createArticle():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get("sKey")
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            if request.method == 'POST':
                try:
                    _trackingId = str(uuid.uuid1())[4:18]
                    _sender = request.form["sender"]
                    _receiver = request.form["receiver"]
                    _articleDesc = request.form["articledesc"]
                    _dangerousGoods = request.form["dangerousgoods"]
                    _deliveryStatus = "PROCESSING"
                    _deliveryList = None
                    c.execute("INSERT INTO lfs_articles \
                    (trackingId, receiverNumber, senderNumber, dangerousGoods, deliveryStatus, deliveryList, articleDesc) \
                    VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (_trackingId, _receiver, _sender, _dangerousGoods, _deliveryStatus, _deliveryList, _articleDesc))
                    consolePrint("createArticle", ("Created Article:", _trackingId))
                    return redirect(url_for("adminArticles"))
                except (ValueError, KeyError, TypeError) as error:
                    consolePrint("createArticles", error)
                return redirect(url_for("adminArticles"))
            else:
                return ("../createArticles does not exist")
        else:
            return redirect(url_for("login"))


@app.route("/admin/customers/createCustomer", methods=["POST"])
def createCustomer():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get("sKey")
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            if request.method == 'POST':
                try:
                    _name = request.form["cname"]
                    _address1 = request.form["address1"]
                    _address2 = request.form["address2"]
                    _suburb = request.form["suburb"]
                    _postcode = request.form["postcode"]
                    _state = request.form["state"]
                    with sqlite3.connect(database) as lfs_db:
                        c = lfs_db.cursor()
                        _existingAddressId = c.execute(
                            "SELECT addressId FROM lfs_addresses WHERE addressLine1=? AND addressLine2=? AND suburb=? AND postcode=? AND state=?",
                            (_address1, _address2, _suburb, _postcode, _state)).fetchone()
                        print(_existingAddressId)
                        if _existingAddressId is None:
                            c.execute("\
                                INSERT INTO lfs_addresses (addressLine1, addressLine2, suburb, postcode, state) VALUES (?, ?, ?, ?, ?)",
                                      (_address1, _address2, _suburb, _postcode, _state)
                                      )
                            _addressId = c.lastrowid

                            c.execute("INSERT INTO lfs_customers (alias, addressId) VALUES (?, ?)", (_name, _addressId))
                            consolePrint("createCustomer", ("Created Customer and Address:", _name))
                        elif _existingAddressId is not None:
                            c.execute("INSERT INTO lfs_customers (alias, addressId) VALUES (?, ?)",
                                      (_name, _existingAddressId))
                            consolePrint("createCustomer", ("Created Customer:", _name))
                        else:
                            consolePrint("createCustomer", "ERROR")
                        return redirect(url_for("adminCustomers"))
                except (ValueError, KeyError, TypeError) as error:
                    consolePrint("createCustomer", error)
                return redirect(url_for("adminCustomers"))
            else:
                return ("../createCustomer does not exist")
        else:
            return redirect(url_for("login"))


@app.route("/logout")
def logout():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get("sKey")
        _response = make_response(redirect(url_for('root')))
        c.execute("UPDATE lfs_users SET currentSession = ? WHERE currentSession = ?", (None, _session,))
        _response.set_cookie('sKey', value="")
        return _response


@app.route("/tracker", methods=["POST", "GET"])
def tracker():
    if request.method == 'POST':
        id = request.form['trackingId']
        if id is None:
            print("Tracker: No ID was given.")
            return redirect(url_for("root"))
        else:
            try:
                with sqlite3.connect(database) as lfs_db:
                    c = lfs_db.cursor()
                    _articles = c.execute("SELECT * FROM lfs_articles WHERE trackingId = ?", (id,)).fetchall()
                    print("ID was Given")
                    print(_articles)
                    return render_template("track.html", article=_articles[0])
            except:
                return redirect(url_for("root"))
    else:
        return redirect(url_for("root"))


@app.route("/customer")
def customer():
    return render_template(template)


@app.route("/dispatch")
def dispatch():
    return render_template(template)


@app.route("/delivery")
def delivery():
    return render_template(template)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("staff/404.html")


if __name__ == '__main__':
    app.run()
