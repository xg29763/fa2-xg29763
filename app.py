# Pre-requisites #
from flask import *
import hashlib, sqlite3, uuid

app = Flask(__name__)
########################################################################################################################
#                                >>>>       Settings for the Flask Interactions      <<<<                              #
########################################################################################################################

###############################
# - HTML Template Variables - #
###############################
template = "lfs-index.html"
loginTemplate = "login.html"
dashboardTemplate = "staff/dashboard.html"

##################################
# - Database Location Variable - #
##################################
database = "data/database.db"

####################################
# 1   - Console Logging Prefix -   #
# 2 - Website Session Cookie Key - #
# 3   - Print Debugging Prints -   #
####################################
appPrefix = "LFS"  # 1
appSCK = "sKey"  # 2
appDebug = True


########################################################################################################################
#                                                                                                                      #
#                                >>>> Application Flask Functions, App Routing, etc. <<<<                              #
#                                                                                                                      #
########################################################################################################################

# Custom Console Printing
def consolePrint(debug, prefix, *message):  # Defines a function that can be accessed from the running program
    if appDebug is False and debug is True:
        return None
    print(appPrefix, "|", prefix, ":", message)  # print() Function prints a string into the console


# Main Root Page App Route
@app.route("/", methods=["GET", "POST"])  # Flask's Application Routing for weblinks. Methods=[] define accepted methods
def root():
    return render_template(template)  # Returns render_template() which will use a predefined html template to display


# Calculator for Weight to Price Estimation
@app.route("/calculator")  # /calculator is the extension that is used on top of the root web url to access this route
def calculator():
    return render_template("calculator.html")  # Returns the calculator.html template


# Unused code.
"""
@app.route("/track", methods=["POST"])
def track():
    if request.method == 'POST':
        _trackingCode = request.form['trackingCode'].encode('utf-8')
        try:
            c.execute("SELECT * FROM lfs_articles WHERE articleNumber = ?", _trackingCode)
"""


##########################################################
# App routing to access the login template through flask #
##########################################################
@app.route("/login", methods=["GET", "POST"])  # App Route that is accessed by ../login with accepted methods GET, POST
def login():
    if request.method == 'POST':  # IF Statement that is checking whether the Methods from the Website is POST
        _email = request.form['email']  # Retrieves the 'email' input from the request form from the /login website
        _password = request.form['password'].encode('utf-8')  # Retrieves the 'password' input from the form from /login
        consolePrint(True, "../login Debug", (_email, _password, hashlib.sha256(_password).hexdigest()))
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
                    consolePrint(True, request.remote_addr, ("Session Created:", _userUuid))
                    # Set the Browser Cookies for userSession and username
                    _response.set_cookie(appSCK, value=_userUuid)
                    return _response
                else:
                    print("Unauthenticated Access")
                    return render_template(loginTemplate)
        except (ValueError, KeyError, TypeError) as error:
            print("Error in Authenticating:", error)
            return render_template(loginTemplate)
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get(appSCK)
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            return redirect(url_for("admin"))
    return render_template(loginTemplate)


###########################################################################################################
# App route for the main staff/employee dashboard page. Shows count of employees, customers and articles. #
###########################################################################################################
@app.route("/admin")
def admin():
    # Verify User Session and Acquire additional user information through cookies
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get(appSCK)
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            try:
                _alias = c.execute("SELECT name FROM lfs_users WHERE currentSession = ?", (_session,))
                _uid = c.execute("SELECT userId FROM lfs_users WHERE currentSession = ?", (_session,))
                _cc = c.execute("SELECT COUNT(*) FROM lfs_customers").fetchone()[0]
                _ec = c.execute("SELECT COUNT(*) FROM lfs_users").fetchone()[0]
                _ac = c.execute("SELECT COUNT(*) FROM lfs_articles").fetchone()[0]
                _n = c.execute("SELECT name FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()[0]
            except:
                consolePrint(True, "Dashboard,", "Possible Unauthenticated Access. SQL?")
                return redirect(url_for('login'))
            consolePrint(True, "Dashboard", "User Authenticated")
            return render_template(dashboardTemplate, customerCount=_cc, employeeCount=_ec, articleCount=_ac, name=_n)
        else:
            consolePrint(True, "Dashboard", "Unauthenticated Access")
            return redirect(url_for('login'))


#####################################################################################################
# App route to the staff/employee article page                                                      #
# Permissions (Inherits permissions from the above role):                                           #
#   - Courier: View articles only, change status from DELIVERING to COMPLETED                       #
#   - LFS Attendant: Create articles, accept goods and check dangerous goods. Tag articles N,E,S,W  #
#   - Manager: Check dangerous goods disclaimer, change status to DELIVERING                        #
#####################################################################################################
@app.route("/admin/articles")
def adminArticles():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get(appSCK)
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


#########################################################################
# App route to the staff/employee employees/account page                #
# Permissions (Inherits permissions from the above role):               #
#   - Courier: NO ACCESS                                                #
#   - LFS Attendant: NO ACCESS                                          #
#   - Manager: Create, View, Delete, Edit Employees and their accounts  #
#########################################################################
@app.route("/admin/employees")
def adminEmployees():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get(appSCK)
        _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
        if _verify is not None:
            try:
                _employees = c.execute("SELECT * FROM lfs_users").fetchall()
                _roles = c.execute("SELECT * FROM lfs_roles").fetchall()
                _n = c.execute("SELECT name FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()[0]
            except:
                return render_template("staff/employees.html")
            return render_template("staff/employees.html", employees=_employees, roles=_roles, name=_n)
        else:
            return redirect(url_for("login"))


#########################################################################
# App route for the staff/employees to the Customers and their details  #
# Permissions (Inherits permissions from the above role):               #
#   - Courier: NO ACCESS                                                #
#   - LFS Attendant: Create, Edit, View customers and Addresses         #
#   - Manager: ^                                                        #
#########################################################################
@app.route("/admin/customers")
def adminCustomers():
    with sqlite3.connect(database) as lfs_db:
        c = lfs_db.cursor()
        _session = request.cookies.get(appSCK)
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


########################################################################################################################
# App routing for variety of actions through POST and GET methods                                                      #
#   - METHOD GET                                                                                                       #
#     > Logout: Logs the currently logged in user through the removal of their local session key and database key      #
#   - METHOD POST                                                                                                      #
#     > Create Customer: Executes a database entry for a customer that contains the information received from the post #
#     > Create Employee: Executes a database entry for a new employee account with related information                 #
#     > Create Article: Executes a database entry for new articles with related info                                   #
########################################################################################################################
@app.route("/admin/action/<act>", methods=["POST", "GET"])
def action(act=None):
    if act is not None:
        with sqlite3.connect(database) as lfs_db:
            c = lfs_db.cursor()
            _session = request.cookies.get(appSCK)
            _verify = c.execute("SELECT * FROM lfs_users WHERE currentSession = ?", (_session,)).fetchone()
            if _verify is not None:
                _userRole = _verify[5]
                if request.method == "GET":
                    if act == "logout":
                        _response = make_response(redirect(url_for('root')))
                        c.execute("UPDATE lfs_users SET currentSession = ? WHERE currentSession = ?", (None, _session,))
                        _response.set_cookie(appSCK, value="")
                        return _response

                if request.method == "POST":
                    if act == "createCustomer":
                        try:
                            _name = request.form["cname"]
                            _address1 = request.form["address1"]
                            _address2 = request.form["address2"]
                            _suburb = request.form["suburb"]
                            _postcode = request.form["postcode"]
                            _state = request.form["state"]
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

                                c.execute("INSERT INTO lfs_customers (alias, addressId) VALUES (?, ?)",
                                          (_name, _addressId))
                                consolePrint(True, "createCustomer", ("Created Customer and Address:", _name))
                            elif _existingAddressId is not None:
                                c.execute("INSERT INTO lfs_customers (alias, addressId) VALUES (?, ?)",
                                          (_name, _existingAddressId))
                                consolePrint(True, "createCustomer", ("Created Customer:", _name))
                            else:
                                consolePrint(False, "createCustomer", "!! ERROR IN CREATING CUSTOMER !!")
                                return redirect(url_for("adminCustomers"))
                        except (ValueError, KeyError, TypeError) as error:
                            consolePrint(False, "createCustomer", error)
                        return redirect(url_for("adminCustomers"))
                    elif act == "createEmployee":
                        try:
                            _name = request.form["ename"]
                            _email = request.form["eemail"]
                            _password = hashlib.sha256(request.form["epass"].encode('utf-8')).hexdigest()
                            _access = request.form["eaccess"]
                            _existingEmail = c.execute("SELECT email FROM lfs_users WHERE email=?",
                                                       (_email,)).fetchone()
                            print(_existingEmail)
                            if _existingEmail is None:
                                c.execute(
                                    "INSERT INTO lfs_users (name, email, username, password, roleId, currentSession) VALUES (?, ?, ?, ?, ?, ?)",
                                    (_name, _email, None, _password, _access, None))
                            else:
                                consolePrint(True, "createEmployee",
                                             "Error creating user account. Does the EMail already exist?")
                                return ("Could not create new account. Email address already exists.")
                        except (ValueError, KeyError, TypeError) as error:
                            consolePrint(False, "createEmployee", error)
                        return redirect(url_for("adminEmployees"))
                    elif act == "createArticle":
                        try:
                            _trackingId = str(uuid.uuid4())[0:16].replace("-",
                                                                          "")  # Replaces all instances of "-" from the UUID and replaces it with nothing
                            _sender = request.form["sender"]
                            _receiver = request.form["receiver"]
                            _articleDesc = request.form["articledesc"]
                            _dangerousGoods = request.form["dangerousgoods"]
                            _deliveryStatus = "PROCESSING"
                            _deliveryList = None
                            c.execute("INSERT INTO lfs_articles \
                            (trackingId, receiverNumber, senderNumber, dangerousGoods, deliveryStatus, deliveryList, articleDesc) \
                            VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (_trackingId, _receiver, _sender, _dangerousGoods, _deliveryStatus, _deliveryList,
                                       _articleDesc))
                            consolePrint(True, "createArticle", ("Created Article:", _trackingId))
                            return redirect(url_for("adminArticles"))
                        except (ValueError, KeyError, TypeError) as error:
                            consolePrint(False, "createArticles", error)
                        return redirect(url_for("adminArticles"))


########################################################
# App routing to the public tracking page for articles #
#   - Accepts the form input of a tracking id          #
########################################################
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


#################################################################
# Handles the 404 Missing Page Error with a customised 404 Page #
#################################################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template("staff/404.html")


################################################
# Runs the flask application when run directly #
################################################
if __name__ == '__main__':
    app.run()
