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
db = SQL("sqlite:///OnlineStore.db")

def GetCategories():
    categories=db.execute("Select * from Categories")
    return categories

@app.route("/")
def index():
    """Show portfolio of stocks"""
    #userid = session["user_id"]
    #rows=db.execute("SELECT * FROM history WHERE id= :userid", userid=userid)
    #usercash=db.execute("SELECT * FROM users WHERE id= :userid", userid=userid)
    categories=GetCategories()
    return render_template("index.html",categories=categories)


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

    #load categories list
    categories=GetCategories()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM Customer WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["Password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["CustomerID"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", categories=categories)


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

    #load categories list
    categories=GetCategories()

    if request.method == "POST":

        #check that all fields are given
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation") or not request.form.get("fname") or not request.form.get("lname") or not request.form.get("address") or not request.form.get("phonenumber"):
            return apology("something is missing!")
        
        #check that passwords match
        if not (request.form.get("password")==request.form.get("confirmation")):
            return apology("password doesn't match")

        #get the fields data
        username = request.form.get("username")
        password = request.form.get("password")
        hashed = generate_password_hash(password, method='sha256', salt_length=8)
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        address = request.form.get("address")
        phonenumber = request.form.get("phonenumber")

        #Check that username doesn't exist
        query = db.execute("SELECT * from Customer WHERE Username= :username", username=request.form.get("username"))
        if len(query) != 0:
            return apology("Username Already Exists", 403)

        #check that phonenumber is digits
        if not phonenumber.isnumeric():
            return apology("Phone Number is not valid")

        #insert the Customer into database
        rows = db.execute("INSERT INTO Customer (Username, Password, FirstName, LastName, Address, PhoneNumber) VALUES(:username, :hashed, :fname, :lname, :address, :phonenumber)", username=username, hashed=hashed, fname=fname, lname=lname, address=address, phonenumber=phonenumber)

        #Get The Generated CustomerID
        query = db.execute("SELECT CustomerID from Customer WHERE Username= :username", username=username)
        id = query[0]["CustomerID"]

        #Check if the id is divisble by 10 to get 100 L.E. Voucher 
        vouchervalue=0
        if (id % 10 == 0):
            vouchervalue=100
        
        #Get Unique Reigsteration Code from ID
        id = str(id)
        registerationcode = generate_password_hash(id, method='sha256', salt_length=6)
        registerationcode = registerationcode[7:13]

        #Update Customer Data
        rows = db.execute("UPDATE Customer SET RegisterationCode= :code, VoucherValue= :value, CodeShares = 10 WHERE Username= :username", code=registerationcode, value=vouchervalue, username=username)

        return render_template("login.html", rows = rows)

    else:
        return render_template("register.html", categories=categories)




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

@app.route("/edituserinfo", methods=["GET", "POST"])
@login_required
def edituserinfo():
    """Edit User Info"""
    
    #load categories list
    categories=GetCategories()

    #Get Current User Info
    rows = db.execute("SELECT * FROM Customer WHERE CustomerID = :id",
                         id=session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        #Check that the user entered his password
        if not request.form.get("password"):
            return apology("Please Enter your password", 403)

        #Check that the entered password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["Password"], request.form.get("password")):
            return apology("Wrong password", 403)

        #Check if he is changing his username
        if request.form.get("uname"):
            query = db.execute("SELECT * from Customer WHERE Username= :username", username=request.form.get("uname"))
            if len(query) != 0:
                return apology("Username Already Exists", 403)
            query = db.execute("UPDATE Customer SET Username= :username WHERE CustomerID= :id",username=request.form.get("uname"), id=session["user_id"])
            return redirect("/edituserinfo")

        #Check if he is changing his name
        if request.form.get("fname") and request.form.get("lname"):
            query = db.execute("UPDATE Customer SET FirstName = :fname, LastName = :lname WHERE CustomerID= :id",fname=request.form.get("fname"),lname=request.form.get("lname"), id=session["user_id"])
            return redirect("/edituserinfo")

        #Check if he is changing his password
        if request.form.get("newpassword") and request.form.get("confirmpassword"):
            if not (request.form.get("newpassword")==request.form.get("confirmpassword")):
                return apology("password doesn't match")
            password = request.form.get("newpassword")
            hashed = generate_password_hash(password, method='sha256', salt_length=8)
            query = db.execute("UPDATE Customer SET Password= :password WHERE CustomerID= :id",password=hashed, id=session["user_id"])
            return redirect("/edituserinfo")

        #Check if he is changing his address
        if request.form.get("address"):
            query = db.execute("UPDATE Customer SET Address = :address WHERE CustomerID= :id",address=request.form.get("address"), id=session["user_id"])
            return redirect("/edituserinfo")
        
        #Check if he is changing his phonenumber
        if request.form.get("phone"):
            if not request.form.get("phone").isnumeric():
                return apology("Phone Number is not valid")
            query = db.execute("UPDATE Customer SET PhoneNumber = :phone WHERE CustomerID= :id",phone=request.form.get("phone"), id=session["user_id"])
            return redirect("/edituserinfo")
        
        return apology("Please fill the whole form")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("edituserinfo.html", categories=categories, row=rows[0])


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
#what a fancy function