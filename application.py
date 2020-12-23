import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    userid = session["user_id"]
    rows=db.execute("SELECT * FROM history WHERE id= :userid", userid=userid)
    usercash=db.execute("SELECT * FROM users WHERE id= :userid", userid=userid)
    return render_template("index.html", rows=rows, usercash=usercash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if lookup(symbol):
            result = lookup(symbol)
            price = result["price"]
            name = result["name"]
            symbol = result["symbol"]
        else:
            return apology("INVALID Symbol")
        shares=int(request.form.get("shares"))
        if shares < 1:
            return apology("Please enter a positive value")
        tprice = shares * price
        userid = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid=userid)
        cash = float(cash[0]["cash"])
        if cash < tprice:
            return apology("Not enough money")
        else:
            result1 = db.execute("UPDATE users SET cash= :newcash WHERE id = :userid", newcash=cash - tprice, userid=userid)
            result2 = db.execute("INSERT INTO history (id, symbol, name, shares, price) VALUES(:userid, :symbol, :name, :shares, :price)", userid=userid, symbol=symbol, name=name, shares=shares, price=tprice)
            return redirect("/")
    else:
        return render_template("buy.html")




@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    return jsonify("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    userid = session["user_id"]
    rows = db.execute("SELECT * FROM history WHERE id= :userid", userid=userid)
    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if lookup(symbol):
            result = lookup(symbol)
            price = result["price"]
            price = usd(price)
            name = result["name"]
            symbol = result["symbol"]
            return render_template("quoterep.html", price = price, name = name, symbol = symbol)
        else:
            return apology("INVALID Symbol")

    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("something is missing!")
        if not (request.form.get("password")==request.form.get("confirmation")):
            return apology("password doesn't match")
        username = request.form.get("username")
        password = request.form.get("password")
        hashed = generate_password_hash(password, method='sha256', salt_length=8)
        rows = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hashed)", username=username, hashed=hashed)
        if not rows:
            return apology("Username already exists")
        return render_template("login.html", rows = rows)

    else:
        return render_template("register.html")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if lookup(symbol):
            result = lookup(symbol)
            price = result["price"]
            name = result["name"]
            symbol = result["symbol"]
        else:
            return apology("INVALID Symbol")
        shares=int(request.form.get("shares"))
        userid = session["user_id"]
        if shares < 1:
            return apology("Please enter a positive value")
        tprice=shares * price
        sym = db.execute("SELECT symbol FROM history WHERE id = :userid", userid=userid)
        cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid=userid)
        cash = float(cash[0]["cash"])
        if not sym:
            return apology("This share is not found")
        else:
            result1 = db.execute("UPDATE users SET cash= :newcash WHERE id = :userid", newcash=cash + tprice, userid=userid)
            result2 = db.execute("INSERT INTO history (id, symbol, name, shares, price) VALUES(:userid, :symbol, :name, :shares, :price)", userid=userid, symbol=symbol, name=name, shares=shares, price=tprice)
            return redirect("/")
    else:
        return render_template("sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)