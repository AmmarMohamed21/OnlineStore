import os
import datetime
import random

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
# from flask_login import current_user
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
#app.jinja_env.filters["usd"] = usd

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

@app.route("/Profile", methods=["GET", "POST"])
@login_required
def Profile():
    categories=GetCategories()
    return render_template("Profile.html",categories=categories) #, rows = rows)

@app.route("/Transactions", methods=["GET", "POST"])
@login_required
def Transactions():
    
        #load categories list
    categories=GetCategories()

    # Get Transaction Info
    rows = db.execute("SELECT * FROM Transactions WHERE CustomerID = :id",
                         id=session["user_id"])

    # Get Customer Info
    CustomerInfo = db.execute("SELECT * FROM Customer WHERE CustomerID = :id",
                        id=session["user_id"])
    
    # Get Tables OF Transactions Contain Product
    TransConPros = []
    for row in rows:
        TransConPros.append(db.execute("SELECT * FROM Transaction_Contains_Products WHERE TransactionID = :id",
        id= row["TransactionID"]))

    # Get All Products IN Transactions
    Product = []
    for TransConPro in TransConPros:
        for row in TransConPro:
            Product.append(db.execute("SELECT * FROM Product WHERE ProductID = :id",
            id= row["ProductID"]))

    # Get Refund
    Refunds = [] 
    for row in rows:
        Refunds.append(db.execute("SELECT * FROM Refunds WHERE TransactionID = :id",
        id= row["TransactionID"]))
    
    # Get Refund Products
    Refund_Product = []
    for Refund in Refunds:
        for Ref in Refund:
            Refund_Product.append(db.execute("SELECT * FROM RefundProducts WHERE RefundID = :id",
            id= Ref["RefundID"]))
        
    # IF User SubMit 
    if request.method == "POST":

        RefQua = int(request.form.get("Refund_Quantity"))
        ProQua = int(request.form.get("Product_Quantity"))
        ProID = int(request.form.get("ProductID"))
        TransID = int(request.form.get("TransactionID"))
        ProPrice =  request.form.get("ProductPrice")
        Trans_Date = request.form.get("Transaction_Date")

        Number = random.randint(1,100)

        Refund_Quantity = db.execute("SELECT Count(Quantity) FROM RefundProducts RP , RefundS R where R.RefundID = RP.RefundID and RP.ProductID = :ProdID and R.TransactionID = :TransaID", 
        ProdID = ProID , TransaID = TransID )######################################

        if RefQua > (ProQua - int(Refund_Quantity[0][1][1]) ):
            return apology(" Refund Quantity > Product Quantity ", 403)

#############################################################################################################
        #  if  datetime.datetime.now().date - Trans_Date > 14:###############################################
        #      return apology(" Refund Date Out 14 Days ", 403)##############################################
        

        db.execute("INSERT INTO Refunds (RefundID, Price, DateRefunded, TransactionID) VALUES (:RID, :ProPeice, :Date , :TransID)", 
        RID = TransID*1000 + ProQua *100 + ProID*10 + RefQua + Number , ProPeice = ProPrice * RefQua , Date = '4/1/2020' , TransID = TransID )######################################

        db.execute("INSERT INTO RefundProducts (RefundID, ProductID, Quantity) VALUES ( :RID, :PID, :Qua)",
        RID = TransID*1000 + ProQua *100 + ProID*10 + RefQua + Number , PID = ProID , Qua = RefQua)


    return render_template("Transactions.html" ,categories=categories,CustomerInfo = CustomerInfo ,
    rows = rows , TransConPros = TransConPros , Product = Product , Refunds = Refunds , Refund_Product =Refund_Product)
      
     
@app.route("/search",methods=["GET","POST"])
def search():
    
    categories=GetCategories()

    # search is the id of the class of the form
    # action="/search" added in layout form
    # name=search in input (not sure if it matters)
    search_for=""
    # # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        sorting_way=request.form.get("sortby")
        search_for=request.form.get("search_for")
    else:
        sorting_way=request.args.get("sortby")
        search_for=request.args.get("search_for")
    if  sorting_way:
        order_by=""
        if sorting_way and search_for:
            if sorting_way=="Date (new first)":
                Products=db.execute(f"SELECT  P.ProductID,ProductName,ProductDescription,P.Price,P.Quantity,InStock,Rating,ImageURL,P.SupplierID,CategoryID "+
                                    f"FROM Product as P,Imports AS I"+
                                    f" WHERE P.ProductID=I.ProductID AND ([ProductName] LIKE '%{search_for}%' or ProductDescription LIKE '%{search_for}%') order by I.DateImported;")
            else:
                if sorting_way=="Price(Low-High)":
                    order_by="Price"
                elif sorting_way=="Price(High-Low)":
                    order_by="Price DESC"
                elif sorting_way=="Rating (5-1)":
                    order_by="Rating DESC" 
                Products = db.execute(f"SELECT * FROM Product WHERE ([ProductName] LIKE '%{search_for}%' or ProductDescription LIKE '%{search_for}%') order by {order_by};")
        else:
            Products=[]
    # Ensure search was submitted
    elif not request.form.get("search"):
        Products=[]
    else:
        # Query database for product 
        pName=request.form.get("search")
        search_for=pName
        Products = db.execute(f"SELECT * FROM Product WHERE ([ProductName] LIKE '%{pName}%' or ProductDescription LIKE '%{pName}%');")
        # return 'You searched for '+ search
        # Redirect user to home page
    
    return render_template("search2.html",Products=Products,categories=categories,search_for=search_for)

    # User reached route via GET (as by clicking a link or via redirect)
    

    
@app.route("/product")
def product():
    categories=GetCategories()
    added_to_cart=request.args.get("addedtocart")
    message="" 
    ok=0
    if added_to_cart:
        if not session:
            message="Login to add to cart"
        else:
            prod_id=request.args.get("prodid")
            value=1
            if prod_id:
                cust_id=session["user_id"]
                availability=db.execute(f"SELECT Quantity FROM Product WHERE ProductID={prod_id} ;")
                if int(value)<=int(availability[0]['Quantity']):
                    Quantity=db.execute(f"SELECT Quantity FROM Customer_Cart WHERE ProductID={prod_id} and CustomerID={cust_id};")
                    if Quantity:
                        ok=db.execute(f"UPDATE Customer_Cart SET Quantity=Quantity+{value} WHERE ProductID={prod_id} and CustomerID={cust_id};")
                    else:
                        ok=db.execute(f"INSERT INTO Customer_Cart VALUES ({prod_id},{cust_id},{value}) ;")
                else:
                    message="Not enough in stock, It is about to finish"
    if request.args.get("prodid"):
        prod_id=request.args.get("prodid")
        Product=db.execute(f"SELECT * FROM Product WHERE ProductID={prod_id};")
        return render_template("product.html",categories=categories,Product=Product,message=message,ok=ok)
    else:
        return redirect("/product")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


@app.route("/PromoCode", methods=["GET", "POST"])
@login_required
def PromoCode():
    """Edit User Info"""
    
    #load categories list
    categories=GetCategories()

    #Get Current User Info
    rows = db.execute("SELECT * FROM Customer WHERE CustomerID = :id",
                         id=session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("code"): #Check it's not empty
             return apology("Please enter Promo Code", 403)

        #Check that the user hasn't entered a promo code before
        if rows[0]["PromoCode"] is not None:
            return apology("You have entered a Promo Code before", 403)

        promo = request.form.get("code")
        #Check the entered code isn't his code
        if rows[0]["RegisterationCode"] == promo :
            return apology("Promo Code isn't valid", 403)
        
        #Check if the promo code exists
        query = db.execute("SELECT * FROM Customer WHERE RegisterationCode= :code", code=promo)
        if len(query) != 1:
            return apology("Promo Code isn't valid", 403)
        
        #Check the number of shares isn't zero
        shares=query[0]["CodeShares"]
        if shares == 0:
            return apology("Promo Code isn't valid", 403)
        
        query = db.execute("UPDATE Customer SET CodeShares=CodeShares-1, VoucherValue = VoucherValue + 50 WHERE RegisterationCode= :code",code=promo)
        query = db.execute("UPDATE Customer SET PromoCode= :code, VoucherValue = VoucherValue + 100 WHERE CustomerID= :id",code=promo, id=session["user_id"])
        return redirect("/PromoCode")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("PromoCode.html", categories=categories, row=rows[0])



#Manage The Store 
@app.route("/management", methods=["GET", "POST"])
def Management():
    """Edit User Info"""
    
    #load categories list
    categories=GetCategories()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        return render_template("management.html", categories=categories)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("management.html", categories=categories)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)




# @app.route("/check", methods=["GET"])
# def check():
#     """Return true if username available, else false, in JSON format"""
#     return jsonify("TODO")


# @app.route("/history")
# @login_required
# def history():
#     """Show history of transactions"""
#     userid = session["user_id"]
#     rows = db.execute("SELECT * FROM history WHERE id= :userid", userid=userid)
#     return render_template("history.html", rows=rows)

# @app.route("/quote", methods=["GET", "POST"])
# @login_required
# def quote():

#     """Get stock quote."""
#     if request.method == "POST":
#         symbol = request.form.get("symbol")
#         if lookup(symbol):
#             result = lookup(symbol)
#             price = result["price"]
#             price = usd(price)
#             name = result["name"]
#             symbol = result["symbol"]
#             return render_template("quoterep.html", price = price, name = name, symbol = symbol)
#         else:
#             return apology("INVALID Symbol")

#     else:
#         return render_template("quote.html")

# @app.route("/sell", methods=["GET", "POST"])
# @login_required
# def sell():
#     """Sell shares of stock"""
#     if request.method == "POST":
#         symbol = request.form.get("symbol")
#         if lookup(symbol):
#             result = lookup(symbol)
#             price = result["price"]
#             name = result["name"]
#             symbol = result["symbol"]
#         else:
#             return apology("INVALID Symbol")
#         shares=int(request.form.get("shares"))
#         userid = session["user_id"]
#         if shares < 1:
#             return apology("Please enter a positive value")
#         tprice=shares * price
#         sym = db.execute("SELECT symbol FROM history WHERE id = :userid", userid=userid)
#         cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid=userid)
#         cash = float(cash[0]["cash"])
#         if not sym:
#             return apology("This share is not found")
#         else:
#             result1 = db.execute("UPDATE users SET cash= :newcash WHERE id = :userid", newcash=cash + tprice, userid=userid)
#             result2 = db.execute("INSERT INTO history (id, symbol, name, shares, price) VALUES(:userid, :symbol, :name, :shares, :price)", userid=userid, symbol=symbol, name=name, shares=shares, price=tprice)
#             return redirect("/")
#     else:
#         return render_template("sell.html")

# @app.route("/buy", methods=["GET", "POST"])
# @login_required
# def buy():
#     """Buy shares of stock"""
#     if request.method == "POST":
#         symbol = request.form.get("symbol")
#         if lookup(symbol):
#             result = lookup(symbol)
#             price = result["price"]
#             name = result["name"]
#             symbol = result["symbol"]
#         else:
#             return apology("INVALID Symbol")
#         shares=int(request.form.get("shares"))
#         if shares < 1:
#             return apology("Please enter a positive value")
#         tprice = shares * price
#         userid = session["user_id"]
#         cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid=userid)
#         cash = float(cash[0]["cash"])
#         if cash < tprice:
#             return apology("Not enough money")
#         else:
#             result1 = db.execute("UPDATE users SET cash= :newcash WHERE id = :userid", newcash=cash - tprice, userid=userid)
#             result2 = db.execute("INSERT INTO history (id, symbol, name, shares, price) VALUES(:userid, :symbol, :name, :shares, :price)", userid=userid, symbol=symbol, name=name, shares=shares, price=tprice)
#             return redirect("/")
#     else:
#         return render_template("buy.html")