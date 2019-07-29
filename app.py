from flask import *
app = Flask(__name__)

template = "lfs.html"


@app.route("/")
def root():
    return render_template(template)


@app.route("/login", methods=["POST"])
def login():
    return render_template(template)


@app.route("/logout")
def logout():
    return render_template(template)


@app.route("/tracker")
def tracker():
    return render_template(template)


@app.route("/customer")
def customer():
    return render_template(template)


@app.route("/dispatch")
def dispatch():
    return render_template(template)


@app.route("/delivery")
def delivery():
    return render_template(template)


app.run(debug=True)

