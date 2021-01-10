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
        ProPrice =  float(request.form.get("ProductPrice"))
        Trans_Date = request.form.get("Transaction_Date")

        Number = random.randint(1,100)

        Refund_Quantity = db.execute("SELECT Count(Quantity) FROM RefundProducts RP , RefundS R where R.RefundID = RP.RefundID and RP.ProductID = :ProdID and R.TransactionID = :TransaID", 
        ProdID = ProID , TransaID = TransID )######################################

        for Refund_Quan in Refund_Quantity:
            for Refund_Qua in Refund_Quan:
                    if Refund_Qua[1] > (ProQua - RefQua) :
                        return apology(" Refund Quantity > Product Quantity ")

#############################################################################################################
        #  if  datetime.datetime.now().date - Trans_Date > 14:###############################################
        #      return apology(" Refund Date Out 14 Days ", 403)##############################################
        

        db.execute("INSERT INTO Refunds (RefundID, Price, DateRefunded, TransactionID) VALUES (:RID, :ProPeice, :Date , :TransID)", 
        RID = TransID*1000 + ProQua *100 + ProID*10 + RefQua + Number , ProPeice = ProPrice * RefQua , Date = '4/1/2020' , TransID = TransID )######################################

        db.execute("INSERT INTO RefundProducts (RefundID, ProductID, Quantity) VALUES ( :RID, :PID, :Qua)",
        RID = TransID*1000 + ProQua *100 + ProID*10 + RefQua + Number , PID = ProID , Qua = RefQua)
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
                message1=f"Not enough in stock"
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
        Products=db.execute(f"SELECT DISTINCT  P.ProductID,ProductName,ProductDescription,P.Price,P.Quantity,InStock,Rating,ImageURL,P.SupplierID,P.CategoryID "+
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



#Manage The Store 
@app.route("/management", methods=["GET", "POST"])
def Management():
    """Edit User Info"""
    
    #load categories list
    categories=GetCategories()
    
    #Get Suppliers Data
    suppliers = db.execute("SELECT * FROM Suppliers order by SupplierName")
    suplocations = db.execute("SELECT S.SupplierName,L.SupplierLocation FROM Suppliers as S, Supplier_Location as L WHERE S.SupplierID=L.SupplierID order by S.SupplierName,L.SupplierLocation")
    products = db.execute("SELECT * FROM Product order by ProductName")
    imports = db.execute("SELECT* FROM Product as P, Suppliers as S, Imports as I WHERE I.SupplierID = S.SupplierID and I.ProductID=P.ProductID order by S.SupplierName, P.ProductName, I.DateImported DESC")
    saleproducts = db.execute("SELECT P.ProductName, S.SalePercentage, S.SaleEndDate FROM Product as P, In_Sale_Products as S WHERE P.ProductID=S.ProductID")
    #Define Password
    ManagementPassword="ronaldinho"

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("password"):
            return apology("Please Enter Management password")

        #Check that the entered password is correct
        if  request.form.get("password") !=  ManagementPassword:
            return apology("Wrong password")
        
        #Check If Insert Category
        if request.form.get("CatNameInsert") and request.form.get("CatURLInsert"):
            url=request.form.get("CatURLInsert")
            if not CheckIMAGEURL(url):
                return apology("URL has to be ending with .jpg or .png")
            query = db.execute("INSERT INTO Categories (CategoryName,url) VALUES (:catname,:caturl)",catname=request.form.get("CatNameInsert"),caturl=request.form.get("CatURLInsert"))
            return redirect("/management")

        #Update Category
        if request.form.get("selectCategoryEdit"):
            selectedCat = request.form.get("selectCategoryEdit")
            if request.form.get("CatURLEdit"):
                url=request.form.get("CatURLEdit")
                if not CheckIMAGEURL(url):
                    return apology("URL has to be ending with .jpg or .png")
                query = db.execute("UPDATE Categories SET url = :url WHERE CategoryName = :selectedCat",selectedCat=selectedCat,url=request.form.get("CatURLEdit")) 
            if request.form.get("CatNameEdit"):
                query = db.execute("UPDATE Categories SET CategoryName = :catname WHERE CategoryName = :selectedCat",selectedCat=selectedCat,catname=request.form.get("CatNameEdit"))
            return redirect("/management")
        
        #Delete Category
        if request.form.get("selectCategoryDelete"):
            query = db.execute("DELETE FROM Categories WHERE CategoryName = :selectedcat",selectedcat=request.form.get("selectCategoryDelete"))
            return redirect("/management")
        
        #Insert Supplier 
        if request.form.get("SupplierNameInsert"):
            query=db.execute("INSERT INTO Suppliers (SupplierName) VALUES(:name)",name=request.form.get("SupplierNameInsert"))
            return redirect("/management")
        
        #Insert Supplier Location
        if request.form.get("selectSupplierInsert") and request.form.get("SupplierLocInsert"):
            supname=request.form.get("selectSupplierInsert")
            suploc=request.form.get("SupplierLocInsert")
            supid = GetSupID(supname)
            query= db.execute("INSERT INTO Supplier_Location VALUES(:suploc,:supid)",supid=supid,suploc=suploc)
            return redirect("/management")

        #Update Supplier Name
        if request.form.get("selectSupplierEdit") and request.form.get("SupplierNameEdit"):
            query = db.execute("UPDATE Suppliers SET SupplierName = :name WHERE SupplierName = :oldname", name=request.form.get("SupplierNameEdit"),oldname=request.form.get("selectSupplierEdit"))
            return redirect("/management")
        
        #Update Supplier Location
        if request.form.get("selectSupLocEdit") and request.form.get("SupLocEdit"):
            text=request.form.get("selectSupLocEdit").split(", ")
            supname=text[0]
            suploc=text[1]
            supid = GetSupID(supname)
            query=db.execute("UPDATE Supplier_Location SET SupplierLocation= :newsuploc WHERE SupplierID= :supid and SupplierLocation= :suploc",suploc=suploc,supid=supid,newsuploc=request.form.get("SupLocEdit"))
            return redirect("/management")

        #Delete Supplier
        if request.form.get("selectSupplierDelete"):
            query= db.execute("DELETE FROM Suppliers WHERE SupplierName= :supname", supname=request.form.get("selectSupplierDelete"))
            return redirect("/management")

        
        #Delete Supplier Location
        if request.form.get("selectSupLocDelete"):
            text=request.form.get("selectSupLocDelete").split(", ")
            supname=text[0]
            suploc=text[1]
            supid = GetSupID(supname)
            query=db.execute("DELETE FROM Supplier_Location WHERE SupplierID= :supid and SupplierLocation= :suploc",supid=supid,suploc=suploc)
            return redirect("/management")

        
        #Insert Product
        if CheckAllProductInsert():
            name = request.form.get("ProdNameInsert")
            desc = request.form.get("ProdDescInsert")
            price = request.form.get("ProdPriceInsert")
            url = request.form.get("ProdURLInsert")
            if not CheckIMAGEURL(url):
                return apology("URL has to be ending with .jpg or .png")
            supname = request.form.get("ProdSupInsert") 
            supid = GetSupID(supname)
            catname = request.form.get("ProdCatInsert")
            catid = GetCatID(catname)
            quantity = 0
            query = db.execute("INSERT INTO Product (ProductName,ProductDescription,Price,Quantity,ImageURL,SupplierID,CategoryID) VALUES (:name,:desc,:price,:quantity,:url,:supid,:catid)",name=name,desc=desc,price=price,quantity=quantity,url=url,supid=supid,catid=catid)
            return redirect("/management")

        #Edit Product 
        if request.form.get("SelectProdEdit"):
            prodname = request.form.get("SelectProdEdit")
            if request.form.get("ProdDescEdit"):
                query=db.execute("UPDATE Product SET ProductDescription= :desc WHERE ProductName= :prodname", desc=request.form.get("ProdDescEdit"), prodname=prodname)
            if request.form.get("ProdURLEdit"):
                url = request.form.get("ProdURLEdit")
                if not CheckIMAGEURL(url):
                    return apology("URL has to be ending with .jpg or .png")
                query=db.execute("UPDATE Product SET ImageURL= :url WHERE ProductName= :prodname", url=url, prodname=prodname)
            if request.form.get("ProdPriceEdit"):
                query=db.execute("UPDATE Product SET Price= :price WHERE ProductName= :prodname", price=request.form.get("ProdPriceEdit"), prodname=prodname)
            if request.form.get("ProdQuantityEdit"):
                query=db.execute("UPDATE Product SET Quantity= :quan WHERE ProductName= :prodname", quan=request.form.get("ProdQuantityEdit"), prodname=prodname)
            if request.form.get("ProdSupEdit"):
                supname=request.form.get("ProdSupEdit")
                supid=GetSupID(supname)
                query=db.execute("UPDATE Product SET SupplierID= :supid WHERE ProductName= :prodname", supid=supid, prodname=prodname)
            if request.form.get("ProdCatEdit"):
                catname=request.form.get("ProdCatEdit")
                catid=GetCatID(catname)
                query=db.execute("UPDATE Product SET CategoryID= :catid WHERE ProductName= :prodname", catid=catid, prodname=prodname)
            if request.form.get("ProdNameEdit"):
                query=db.execute("UPDATE Product SET ProductName= :name WHERE ProductName= :prodname", name=request.form.get("ProdNameEdit"), prodname=prodname)
            return redirect("/management")

        #Delete Product
        if request.form.get("SelectProdDelete"):
            query=db.execute("DELETE FROM Product WHERE ProductName= :name", name=request.form.get("SelectProdDelete"))
            return redirect("/management")

        #ADD Import
        if request.form.get("ImportSupInsert") and request.form.get("ImportProdInsert") and request.form.get("ImportPriceInsert") and request.form.get("ImportQuanInsert") and request.form.get("ImportDateInsert"):
            supname=request.form.get("ImportSupInsert")
            prodname=request.form.get("ImportProdInsert")
            supid=GetSupID(supname)
            prodid=GetProdID(prodname)
            query = db.execute("SELECT SupplierID FROM Product WHERE ProductID=:prodid",prodid=prodid)
            if len(query) != 1:
                return apology("Something Went Wrong")
            realsupid = query[0]["SupplierID"]
            if realsupid != supid:  #Preventing from Inserting if the supplier is different
                return apology("This Product has a different Supplier")
            price = request.form.get("ImportPriceInsert")
            quantity = request.form.get("ImportQuanInsert")
            date = request.form.get("ImportDateInsert")
            query = db.execute("INSERT INTO Imports VALUES(:date, :supid, :prodid, :quantity, :price)",date=date,supid=supid,prodid=prodid,quantity=quantity,price=price)
            query = db.execute("UPDATE Product SET Quantity=Quantity+:quantity WHERE ProductID=:prodid",quantity=quantity,prodid=prodid)
            return redirect("/management")
        
        #Delete Imports
        if request.form.get("ImportDelete"):
            text=request.form.get("ImportDelete").split(", ")
            supname=text[0]
            prodname=text[1]
            date=text[2]
            supid=GetSupID(supname)
            prodid=GetProdID(prodname)
            query=db.execute("SELECT Quantity FROM Imports WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",supid=supid,prodid=prodid,date=date)
            if len(query) != 1:
                return apology("Something Wrong")
            quantity=query[0]["Quantity"]
            query=db.execute("SELECT Quantity FROM Product WHERE ProductID= :prodid",prodid=prodid)
            oldquantity=query[0]["Quantity"]
            newquantity = oldquantity - quantity
            if newquantity<0:
                return apology("You can't delete this Import, not enough products")
            query = db.execute("UPDATE Product SET Quantity = :newquantity WHERE ProductID = :prodid", newquantity=newquantity, prodid=prodid)
            query = db.execute("DELETE FROM Imports WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",supid=supid,prodid=prodid,date=date)
            return redirect("/management")

        #Edit Import
        if request.form.get("ImportsEdit"):
            text=request.form.get("ImportsEdit").split(", ")
            supname=text[0]
            prodname=text[1]
            date=text[2]
            supid=GetSupID(supname)
            prodid=GetProdID(prodname)
            query=db.execute("SELECT Quantity FROM Imports WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",supid=supid,prodid=prodid,date=date)
            if len(query) != 1:
                return apology("Something Wrong")
            oldquantity=query[0]["Quantity"]
            query=db.execute("SELECT Quantity FROM Product WHERE ProductID= :prodid",prodid=prodid)
            productquantity=query[0]["Quantity"]
            if request.form.get("ImportPriceEdit"):
                query=db.execute("UPDATE Imports SET Price= :price WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",price=request.form.get("ImportPriceEdit"),supid=supid,prodid=prodid,date=date)
            if request.form.get("ImportQuanEdit"):
                addedquantity=request.form.get("ImportQuanEdit")
                newquantity = productquantity - oldquantity + int(addedquantity)
                if newquantity < 0:
                    return apology("Quantity isn't valid, not enough products")
                query = db.execute("UPDATE Product SET Quantity = :newquantity WHERE ProductID = :prodid", newquantity=newquantity, prodid=prodid)
                query=db.execute("UPDATE Imports SET Quantity= :quan WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",quan=addedquantity,supid=supid,prodid=prodid,date=date)
            return redirect("/management")

        # Sale Insert
        if request.form.get("SaleProdInsert") and request.form.get("SalePercentInsert") and request.form.get("SaleDateInsert"):
            prodname=request.form.get("SaleProdInsert")
            prodid = GetProdID(prodname)
            query = db.execute("SELECT * FROM In_Sale_Products WHERE ProductID = :prodid",prodid=prodid)
            if len(query) != 0:
                return apology("This Product is already in Sale")
            query = db.execute("INSERT INTO In_Sale_Products VALUES(:percent,:date,:prodid)",percent=request.form.get("SalePercentInsert"),date=request.form.get("SaleDateInsert"),prodid=prodid)
            return redirect("/management")

        #Sale Edit
        if request.form.get("SaleProdEdit"):
            prodname=request.form.get("SaleProdEdit")
            prodid = GetProdID(prodname)
            if request.form.get("SalePercentEdit"):
                query = db.execute("UPDATE In_Sale_Products SET SalePercentage=:percent WHERE ProductID= :prodid",percent=request.form.get("SalePercentEdit"),prodid=prodid)
            if request.form.get("SaleDateEdit"):
                query = db.execute("UPDATE In_Sale_Products SET SaleEndDate=:date WHERE ProductID= :prodid",date=request.form.get("SaleDateEdit"),prodid=prodid)
            return redirect("/management")
        
        #Sale Delete
        if request.form.get("SaleProdDelete"):
            prodname=request.form.get("SaleProdDelete")
            prodid = GetProdID(prodname)
            query=db.execute("DELETE FROM In_Sale_Products WHERE ProductID= :prodid",prodid=prodid)
            return redirect("/management")

        #POST WAS UNSUCCESFUL    
        return apology("Something Missing")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("management.html", categories=categories,suppliers=suppliers,suplocations=suplocations,products=products, imports=imports, saleproducts=saleproducts)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# this function is for cart
@app.route("/cart", methods=["GET", "POST"])
def cart():

    if(request.method == "POST"):
        if "remove" in request.form:
            productId = int(request.form.get("productId"))
            db.execute("delete from Customer_Cart where ProductID = :id and CustomerID = :customer", id = productId, customer = session["user_id"])
        elif "edit" in request.form:
            productId = int(request.form.get("productId"))
            quantity = int(request.form.get("editQuantity"))
            db.execute("update Customer_Cart set Quantity = :q where CustomerID = :id and ProductID = :pid", q = quantity, id = session['user_id'], pid = productId)
        elif "confirmPayment" in request.form:
            totalPrice = db.execute("select sum(Price * C.Quantity) from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
            count = totalPrice[0]["sum(Price * C.Quantity)"]
            productsCustomer = db.execute("select P.ProductID, P.ProductDescription, P.ImageURL, P.ProductName, C.Quantity from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
            # get the local date
            today = date.today().strftime("%d/%m/%y")

            # get the payment method
            paymentMethod = request.form.get("btnradio")
            # query to put the products within cart into transaction
            db.execute("insert into Transactions(TransactionDate, IsDelivered, Price, PaymentMethod, CustomerID) values(:date, false, :price, :paymentmethod, :id)", date = today, price = count, paymentmethod = paymentMethod, id = session['user_id'])
            # get the the transaction id 
            transactionId = db.execute("select max(TransactionID) from Transactions")[0]["max(TransactionID)"]
            # this loop for insert every product into transaction_contains_product
            for i in productsCustomer:
                db.execute("insert into Transaction_Contains_Products values(:trId, :pId, :q)", trId = transactionId, pId = i["ProductID"], q = i["Quantity"])
            # delete the items in the cart
            db.execute("delete from Customer_Cart where CustomerID = :id", id = session['user_id'])


    
    

    
    productsCustomer = db.execute("select P.ProductID, P.ProductDescription, P.ImageURL, P.ProductName, C.Quantity from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
    productsQuantity = db.execute("select Quantity from Customer_Cart where CustomerID = :id", id=session["user_id"])
    productsCount = db.execute("select count(ProductID) from Customer_Cart where CustomerID = :id", id=session["user_id"])
    totalPrice = db.execute("select sum(Price * C.Quantity) from Product as P, Customer_Cart as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])
    count = totalPrice[0]["sum(Price * C.Quantity)"]
    productsCount = productsCount[0]["count(ProductID)"]

    return render_template("Cart.html", products = productsCustomer, productsQuantity = productsQuantity, count = productsCount, totalPrice = count)

@app.route("/wishlist", methods = ["GET", "POST"])
def wishlist():

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
            db.execute("insert into Customer_Cart values (:pId, :id, 1)", pId = productId, id = session['user_id'])
            # then delete it from the wish list
            db.execute("delete from Customer_Wishlist where CustomerID = :id and ProductID = :pId", id = session['user_id'], pId = productId)
        # if the clicked button is add all to cart
        elif "allToCart" in request.form:
            # get all products in the wish list
            productsInWishlist = db.execute("select ProductID from Customer_Wishlist where CustomerID = :id", id = session['user_id'])
            # loop for every product to insert it into cart
            for i in productsInWishlist:
                db.execute("insert into Customer_Cart values (:pId, :id, 1)", pId = i["ProductID"], id = session['user_id'])
            # delete the products from the wish list
            db.execute("delete from Customer_Wishlist where CustomerID = :id", id = session['user_id'])

    # get the products in the wishlist of the customer
    productsCustomer = db.execute("select * from Product as P, Customer_Wishlist as C where C.CustomerID = :id and P.ProductID = C.ProductID", id=session["user_id"])

    # get the count of the items in the wishlist
    productsCount = db.execute("select count(ProductID) from Customer_Wishlist where CustomerID = :id", id=session["user_id"])
    productsCount = productsCount[0]["count(ProductID)"]
    return render_template("/wishlist.html", products = productsCustomer, count = productsCount)

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