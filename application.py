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
from datetime import date
from helpers import apology, login_required, CheckIMAGEURL

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


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///OnlineStore.db")

def GetCategories():
    categories=db.execute("Select * from Categories order by CategoryName")
    today = date.today()
    #Remove Sale From which the sale ended
    saleproducts = db.execute("SELECT * FROM In_Sale_Products")
    for product in saleproducts:
        prodid=product["ProductID"]
        productdate = product["SaleEndDate"].split("-")
        productdate = date(int(productdate[0]),int(productdate[1]),int(productdate[2]))
        if productdate < today:
            query = db.execute("DELETE FROM In_Sale_Products WHERE ProductID= :prodid",prodid=prodid)
    return categories

@app.route("/")
def index():
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
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM Customer WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["Password"], request.form.get("password")):
            return apology("invalid username and/or password")

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
            return apology("Username Already Exists")

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
            return apology("Please Enter your password")

        #Check that the entered password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["Password"], request.form.get("password")):
            return apology("Wrong password")

        #Check if he is changing his username
        if request.form.get("uname"):
            query = db.execute("SELECT * from Customer WHERE Username= :username", username=request.form.get("uname"))
            if len(query) != 0:
                return apology("Username Already Exists")
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
        TransConPros.append(db.execute("SELECT T.TransactionID, T.ProductID, T.Quantity, P.ProductName, P.ProductID, T.BuyPrice FROM Transaction_Contains_Products as T, Product as P WHERE T.TransactionID = :id and T.ProductID=P.ProductID",
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
            Refund_Product.append(db.execute("SELECT R.RefundID, R.ProductID, R.Quantity, P.ProductName, R.Price, P.ProductID FROM RefundProducts as R, Product as P WHERE RefundID = :id and R.ProductID=P.ProductID",
            id= Ref["RefundID"]))
        
    # IF User SubMit 
    if request.method == "POST":
        mark_as_delivered_ID=request.form.get("TransactionID_delivered")
        if mark_as_delivered_ID:
            db.execute(f"UPDATE Transactions SET IsDelivered=1 WHERE TransactionID={mark_as_delivered_ID}")
            today=date.today()
            # db.execute(f"INSERT INTO Deliveries(DateDelivered,TransactionID) VALUES('{today.year}-{today.month}-{today.day}',{mark_as_delivered_ID}) ")
            db.execute(f"UPDATE Deliveries SET DateDelivered='{today.year}-{today.month}-{today.day}' WHERE TransactionID={mark_as_delivered_ID} ")
        else:
            RefQua = int(request.form.get("Refund_Quantity"))
            ProQua = int(request.form.get("Product_Quantity"))
            ProID = int(request.form.get("ProductID"))
            TransID = int(request.form.get("TransactionID"))
            ProPrice =  float(request.form.get("ProductPrice"))
            Trans_Date = str(request.form.get("Transaction_Date"))

            Number = random.randint(1,100)

            Refund_Quantity = ( db.execute("SELECT Count(Quantity) FROM RefundProducts RP , RefundS R where R.RefundID = RP.RefundID and RP.ProductID = :ProdID and R.TransactionID = :TransaID", 
            ProdID = ProID , TransaID = TransID ))######################################
            
            if Refund_Quantity[0]['Count(Quantity)'] > (ProQua - RefQua):
                return apology(" Refund Quantity > Product Quantity ")

            Trans_Date1 = Trans_Date + " 0:0:0"
            format = "%Y-%m-%d %H:%M:%S"
            Trans_Date2 = datetime.datetime.strptime(Trans_Date1,format)
            TransDate14 = Trans_Date2 + datetime.timedelta(days = 14)
            CurrentDate = datetime.datetime.now().date()

            if  CurrentDate > TransDate14.date():##############################################
                return apology(" Refund Date Out 14 Days ")
            

            db.execute("INSERT INTO Refunds (RefundID, Price, DateRefunded, TransactionID) VALUES (:RID, :ProPeice, :Date , :TransID)", 
            RID = TransID*1000 + ProQua *100 + ProID*10 + RefQua + Number , ProPeice = ProPrice * RefQua , Date = datetime.datetime.now().date() , TransID = TransID )######################################

            db.execute("INSERT INTO RefundProducts (RefundID, ProductID, Quantity, Price) VALUES ( :RID, :PID, :Qua, :price)",
            RID = TransID*1000 + ProQua *100 + ProID*10 + RefQua + Number , PID = ProID , Qua = RefQua, price=ProPrice)

            db.execute("UPDATE Product SET Quantity = Quantity + :ref WHERE ProductID=:proid", ref=RefQua, proid=ProID )
        return redirect("/Transactions")

    return render_template("Transactions.html" ,categories=categories,CustomerInfo = CustomerInfo ,
    rows = rows , TransConPros = TransConPros , Product = Product , Refunds = Refunds , Refund_Product =Refund_Product)
      
     
@app.route("/search",methods=["GET","POST"])
def search():
    sale=[]
    new_price=[]
    categories=GetCategories()
    search_for=""
    if request.method == "POST":
        sorting_way=request.form.get("sortby")
        search_for=request.form.get("search")
    else:
        sorting_way=request.args.get("sortby")
        search_for=request.args.get("search_for")
    order_by=""
    if sorting_way and search_for:
        if sorting_way=="Date (new first)":
            Products=db.execute(f"SELECT  P.ProductID,ProductName,ProductDescription,P.Price,P.Quantity,Rating,ImageURL,P.SupplierID,CategoryID "+
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
    elif search_for:
        Products = db.execute(f"SELECT * FROM Product WHERE ([ProductName] LIKE '%{search_for}%' or ProductDescription LIKE '%{search_for}%');")

    else:
        Products=[]
 
    for i in range(len(Products)):
        temp=db.execute(f"select SalePercentage from In_Sale_Products WHERE ProductID={Products[i]['ProductID']}")
        temp2=None
        if temp:
            temp2=round((100-float(temp[0]['SalePercentage']))/100*float(Products[i]['Price']))
            sale.append(temp)
            new_price.append(temp2)
        else:
            sale.append(None)
            new_price.append(None)
    return render_template("search.html",Products=Products,categories=categories,search_for=search_for,sale=sale,new_price=new_price)


    
@app.route("/product",methods=['POST','GET'])
def product():
    # jinja2 parameters initialization,, productID is assumed to be sent using get, none may be initialized later
    categories=GetCategories()
    prod_id=request.args.get("prodid")
    added_to_cart=request.form.get("ProductID-addtocart")
    added_to_wishlist=request.form.get("ProductID-addtowishlist")
    delete_rating=request.args.get("del_rating")
    Product=[]
    sale=None
    if added_to_cart:
        prod_id=added_to_cart
    if added_to_wishlist:
        prod_id=added_to_wishlist
    if prod_id:
        Product=db.execute(f"SELECT * FROM Product WHERE ProductID={prod_id}")
        sale=db.execute(f"select SalePercentage from In_Sale_Products WHERE ProductID={prod_id}")
    new_price=None

    message1=None
    message2=None
    ok1=None
    ok2=None
    cust_id=None
    current_rating=None
    current_user_rating=None
    new_user_rating=None
    supplier=db.execute(f"SELECT SupplierName FROM Suppliers as S,Product as P WHERE S.SupplierID=P.SupplierID AND P.ProductID={prod_id}")
    #put values in parameters - new rating, added_to_cart, added_to_wishlist
    if session:
        cust_id=session["user_id"]
        current_user_rating=db.execute(f"SELECT Rating FROM Customer_Rates_Products WHERE CustomerID={cust_id} AND ProductID={prod_id}")
        if current_user_rating:
            current_user_rating=current_user_rating[0]['Rating']
        new_user_rating=request.args.get("star")
        if new_user_rating:
            if current_user_rating:
                db.execute(f"UPDATE Customer_Rates_Products SET Rating={new_user_rating} WHERE  CustomerID={cust_id} AND ProductID={prod_id}")
                current_user_rating=new_user_rating
            else:
                db.execute(f"INSERT INTO Customer_Rates_Products VALUES({prod_id},{cust_id},{new_user_rating})")
                current_user_rating=new_user_rating
        if added_to_cart:
            value=int(request.form.get("quantity"))
            availability=db.execute(f"SELECT Quantity FROM Product WHERE ProductID={prod_id} ")
            if int(value)<=int(availability[0]['Quantity']):
                Quantity=db.execute(f"SELECT Quantity FROM Customer_Cart WHERE ProductID={prod_id} and CustomerID={cust_id}")
                if Quantity:
                    ok1=db.execute(f"UPDATE Customer_Cart SET Quantity=Quantity+{value} WHERE ProductID={prod_id} and CustomerID={cust_id}")
                else:
                    ok1=db.execute(f"INSERT INTO Customer_Cart VALUES ({prod_id},{cust_id},{value})")
            else:
                message1="Not enough in stock"
        if added_to_wishlist:
            num=db.execute(f"SELECT * FROM Customer_Wishlist WHERE ProductID={prod_id} and CustomerID={cust_id}")
            if not num:
                ok2=db.execute(f"INSERT INTO Customer_Wishlist VALUES ({cust_id},{prod_id})")
            else:
                message2="Already in the wishlist"
        if delete_rating:
            db.execute(f"DELETE FROM Customer_Rates_Products WHERE ProductID={prod_id} AND CustomerID={cust_id}")
            current_user_rating=None
    else:
        if added_to_cart:
            message1="Please Login to add to cart"
        if added_to_wishlist:
            message2="Please Login to add to wishlist"
    if sale:
        new_price=round((100-float(sale[0]['SalePercentage']))/100*float(Product[0]['Price']))
    current_rating=db.execute(f"SELECT AVG(Rating) FROM Customer_Rates_Products WHERE ProductID={prod_id}")
    number_of_rates=db.execute(f"SELECT COUNT(Rating) FROM Customer_Rates_Products WHERE ProductID={prod_id}")
    number_of_rates=number_of_rates[0]['COUNT(Rating)']
    if number_of_rates:
        db.execute(f"UPDATE Product SET Rating={current_rating[0]['AVG(Rating)']} WHERE ProductID={prod_id}")
        current_rating=round(current_rating[0]['AVG(Rating)'],2)
    else:
        db.execute(f"UPDATE Product SET Rating=0 WHERE ProductID={prod_id}")
    if session and added_to_cart:
        if message1 !="Not enough in stock":
            return redirect(f"/product?prodid={prod_id}")

    return render_template("product.html",categories=categories,Product=Product,message1=message1,ok1=ok1,message2=message2,ok2=ok2,sale=sale,new_price=new_price,current_user_rating=current_user_rating,current_rating=current_rating,number_of_rates=number_of_rates,supplier=supplier)





@app.route("/category",methods=["GET","POST"])
def category():
    categories=GetCategories()
    sale=[]
    new_price=[]
    cat_id=request.args.get("categoryid")
    if cat_id:
        Category=db.execute(f"Select * from Categories WHERE [CategoryID]={cat_id}")
        Products=db.execute(f"SELECT DISTINCT  P.ProductID,ProductName,ProductDescription,P.Price,P.Quantity,Rating,ImageURL,P.SupplierID,P.CategoryID "+
        f"FROM Product as P,Categories AS C"+
        f" WHERE P.CategoryID={cat_id} ;")
        for i in range(len(Products)):
            temp=db.execute(f"select SalePercentage from In_Sale_Products WHERE ProductID={Products[i]['ProductID']}")
            temp2=None
            if temp:
                temp2=round((100-float(temp[0]['SalePercentage']))/100*float(Products[i]['Price']))
                sale.append(temp)
                new_price.append(temp2)
            else:
                sale.append(None)
                new_price.append(None)
        return  render_template("category.html",categories=categories,Products=Products,Category=Category,sale=sale,new_price=new_price)
    else:
        return redirect('/')



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name)


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
             return apology("Please enter Promo Code")

        #Check that the user hasn't entered a promo code before
        if rows[0]["PromoCode"] is not None:
            return apology("You have entered a Promo Code before")

        promo = request.form.get("code")
        #Check the entered code isn't his code
        if rows[0]["RegisterationCode"] == promo :
            return apology("Promo Code isn't valid")
        
        #Check if the promo code exists
        query = db.execute("SELECT * FROM Customer WHERE RegisterationCode= :code", code=promo)
        if len(query) != 1:
            return apology("Promo Code isn't valid")
        
        #Check the number of shares isn't zero
        shares=query[0]["CodeShares"]
        if shares == 0:
            return apology("Promo Code isn't valid")
        
        query = db.execute("UPDATE Customer SET CodeShares=CodeShares-1, VoucherValue = VoucherValue + 50 WHERE RegisterationCode= :code",code=promo)
        query = db.execute("UPDATE Customer SET PromoCode= :code, VoucherValue = VoucherValue + 100 WHERE CustomerID= :id",code=promo, id=session["user_id"])
        return redirect("/PromoCode")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("PromoCode.html", categories=categories, row=rows[0])


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# this function is for cart
@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():

    categories=GetCategories()

    if(request.method == "POST"):
        if "remove" in request.form:
            productId = int(request.form.get("productId"))
            db.execute("delete from Customer_Cart where ProductID = :id and CustomerID = :customer", id = productId, customer = session["user_id"])
        elif "edit" in request.form:
            productId = int(request.form.get("productId"))
            quantity = int(request.form.get("editQuantity"))
            db.execute("update Customer_Cart set Quantity = :q where CustomerID = :id and ProductID = :pid", q = quantity, id = session['user_id'], pid = productId)
        elif "confirmPayment" in request.form:
            count = db.execute("select count(ProductID) from Customer_Cart where CustomerID = :id", id = session['user_id'])[0]["count(ProductID)"]
            if count:
                #get the customer cart products
                productsCustomer = db.execute("select P.ProductID, P.ProductDescription, P.ImageURL, P.ProductName, C.Quantity, P.Price from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
                for i in productsCustomer:
                    #get the total quantity of the product
                    totalProductQuantity = db.execute("select Quantity from Product where ProductID = :id", id = i["ProductID"])[0]["Quantity"]
                    if totalProductQuantity < i["Quantity"]:
                        pName = i["ProductName"]
                        q = str(totalProductQuantity)
                        return apology("Not enough quantity of " + pName + " Max Quantity is " + q)

                totalPrice = db.execute("select sum(Price * C.Quantity) from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
                count = totalPrice[0]["sum(Price * C.Quantity)"]
                # get the local date
                today = date.today().strftime("%Y-%m-%d")
                # check for voucher value
               
                # get the payment method
                paymentMethod = request.form.get("btnradio")
                # query to put the products within cart into transaction
                db.execute("insert into Transactions(TransactionDate, IsDelivered, Price, PaymentMethod, CustomerID) values(:date, false, :price, :paymentmethod, :id)", date = today, price = count, paymentmethod = paymentMethod, id = session['user_id'])
                # get the the transaction id 
                transactionId = db.execute("select max(TransactionID) from Transactions")[0]["max(TransactionID)"]
                # insert the transaction into deliveries
                db.execute("insert into Deliveries (TransactionID) values (:t)", t = transactionId)
                # this loop for insert every product into transaction_contains_product
                for i in productsCustomer:
                    # calculate the percentage of the sale
                    Percentage = db.execute("select SalePercentage from In_Sale_Products where ProductID = :id", id = i["ProductID"])
                    if not Percentage:
                        db.execute("insert into Transaction_Contains_Products values(:trId, :pId, :q, :b)", trId = transactionId, pId = i["ProductID"], q = i["Quantity"], b = i["Price"])
                    else:
                        Percentage = Percentage[0]["SalePercentage"] / 100
                        PriceAfterSale = round(i["Price"] - i["Price"] * Percentage,2)
                        db.execute("insert into Transaction_Contains_Products values(:trId, :pId, :q, :b)", trId = transactionId, pId = i["ProductID"], q = i["Quantity"], b = PriceAfterSale)
                    # update the quantity in the Product
                    db.execute("update Product set Quantity = Quantity - :q where ProductID = :id", q = i["Quantity"], id = i["ProductID"])
                    # delete the items in the cart
                db.execute("delete from Customer_Cart where CustomerID = :id", id = session['user_id'])
                # update the transaction after sale
                
                    # get the total price after sale from transaction contains products
                totalPriceAfterSale = db.execute("select sum(BuyPrice*Quantity) from Transaction_Contains_Products where TransactionID = :id", id = transactionId)[0]["sum(BuyPrice*Quantity)"]
                # the voucher value
                voucher = db.execute("select VoucherValue from Customer where CustomerID = :id", id = session['user_id'])
                voucher = voucher[0]["VoucherValue"]
                # get the value of the check button
                voucherButton = request.form.get("voucher")
                # check if the voucher button is pressed
                if voucherButton:
                    if totalPriceAfterSale >= voucher:
                        totalPriceAfterSale = totalPriceAfterSale - voucher
                        # delete the voucher value or make it zero in the data base
                        db.execute("update Customer set VoucherValue = 0 where CustomerID = :id", id = session['user_id'])
                    else:
                        voucher -= totalPriceAfterSale
                        totalPriceAfterSale = 0
                        db.execute("update Customer set VoucherValue = :v where CustomerID = :id", id = session['user_id'], v = voucher)
                # update the transaction
                db.execute("update Transactions set Price = :p where TransactionID = :id", p = totalPriceAfterSale, id = transactionId)

        

    
            

    

    
    productsCustomer = db.execute("select P.ProductID, P.ProductDescription, P.ImageURL, P.ProductName, C.Quantity, P.Price from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
    # code to get the real total price of the products
    total = 0
    for i in productsCustomer:
        perc = db.execute("select SalePercentage from In_Sale_Products where ProductID = :id", id = i["ProductID"])
        if not perc:
            total += int(i["Price"]) * i["Quantity"]
        else:
            perc = perc[0]["SalePercentage"] / 100
            PafterSale = i["Price"] - i["Price"] * perc
            total += PafterSale * i["Quantity"]
    productsCount = db.execute("select count(ProductID) from Customer_Cart where CustomerID = :id", id=session["user_id"])
    totalPrice = db.execute("select sum(Price * C.Quantity) from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
    productsCount = productsCount[0]["count(ProductID)"]

    return render_template("Cart.html", products = productsCustomer, count = productsCount, totalPrice = round(total,2),categories=categories)

@app.route("/wishlist", methods = ["GET", "POST"])
@login_required
def wishlist():
    categories=GetCategories()
    # confirm the post requests
    if(request.method == "POST"):
        #if the clicked button is remove
        if "remove" in request.form:
            productId = int(request.form.get("productId"))
            db.execute("delete from Customer_Wishlist where CustomerID = :id and ProductID = :pId", id = session['user_id'], pId = productId)
        # if the clicked button is add to cart
        elif "addToCart" in request.form:
            # add the item to cart
            productId = int(request.form.get("productId"))
            quantity = db.execute("select Quantity from Customer_Cart where ProductID = :id and CustomerID = :cid", id = productId, cid = session['user_id'])[0]["Quantity"]
            if quantity:
                db.execute("update Customer_Cart set Quantity = Quantity + 1 where CustomerID = :cid and ProductID = :id", cid = session['user_id'], id = productId)
            else:
                db.execute("insert into Customer_Cart values (:pId, :id, 1)", pId = productId, id = session['user_id'])
            # then delete it from the wish list
            db.execute("delete from Customer_Wishlist where CustomerID = :id and ProductID = :pId", id = session['user_id'], pId = productId)
        # if the clicked button is add all to cart
        elif "allToCart" in request.form:
            # get all products in the wish list
            productsInWishlist = db.execute("select ProductID from Customer_Wishlist where CustomerID = :id", id = session['user_id'])
            # loop for every product to insert it into cart
            for i in productsInWishlist:
                quantity = db.execute("select Quantity from Customer_Cart where ProductID = :id and CustomerID = :cid", id = i["ProductID"], cid = session['user_id'])
                if quantity:
                    db.execute("update Customer_Cart set Quantity = Quantity + 1 where CustomerID = :cid and ProductID = :id", cid = session['user_id'], id = i["ProductID"])
                else:
                    db.execute("insert into Customer_Cart values (:pId, :id, 1)", pId = i["ProductID"], id = session['user_id'])
            # delete the products from the wish list
            db.execute("delete from Customer_Wishlist where CustomerID = :id", id = session['user_id'])

    # get the products in the wishlist of the customer
    productsCustomer = db.execute("select * from Product as P, Customer_Wishlist as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])

    # get the count of the items in the wishlist
    productsCount = db.execute("select count(ProductID) from Customer_Wishlist where CustomerID = :id", id=session["user_id"])
    productsCount = productsCount[0]["count(ProductID)"]
    return render_template("/wishlist.html", products = productsCustomer, count = productsCount,categories=categories)

def CheckAllProductInsert():
    if request.form.get("ProdNameInsert") and request.form.get("ProdDescInsert") and request.form.get("ProdPriceInsert") and request.form.get("ProdURLInsert") and request.form.get("ProdCatInsert") and request.form.get("ProdSupInsert"):
        return True 
    return False

def GetSupID (supname):
    query=db.execute("SELECT * FROM Suppliers WHERE SupplierName= :supname",supname=supname)
    if len(query) != 1:
        return apology("Somthing Missing")
    supid=query[0]["SupplierID"]
    return supid

def GetCatID (catname):
    query=db.execute("SELECT * FROM Categories WHERE CategoryName= :catname",catname=catname)
    if len(query) != 1:
        return apology("Somthing Missing")
    catid=query[0]["CategoryID"]
    return catid

def GetProdID (prodname):
    query=db.execute("SELECT * FROM Product WHERE ProductName= :prodname",prodname=prodname)
    if len(query) != 1:
        return apology("Somthing Missing")
    prodid=query[0]["ProductID"]
    return prodid
