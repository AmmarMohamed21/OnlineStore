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
from helpers import empapology, login_required, CheckIMAGEURL

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



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return empapology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return empapology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM Employees WHERE Username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["Password"], request.form.get("password")):
            return empapology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["EmployeeID"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("emplogin.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    """Register Employee"""

    if request.method == "POST":

        #check that all fields are given
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation") or not request.form.get("name") :
            return empapology("something is missing!")
        
        #check that passwords match
        if not (request.form.get("password")==request.form.get("confirmation")):
            return empapology("password doesn't match")

        #get the fields data
        username = request.form.get("username")
        password = request.form.get("password")
        hashed = generate_password_hash(password, method='sha256', salt_length=8)
        name = request.form.get("name")
       

        #Check that username doesn't exist
        query = db.execute("SELECT * from Employees WHERE Username= :username", username=request.form.get("username"))
        if len(query) != 0:
            return empapology("Username Already Exists")

        #insert the Customer into database
        rows = db.execute("INSERT INTO Employees (Username, Password, Name) VALUES(:username, :hashed, :name)", username=username, hashed=hashed, name=name)

        return redirect("/register")

    else:
        return render_template("regemployee.html")


@app.route("/Profile", methods=["GET", "POST"])
@login_required
def edituserinfo():
    """Edit User Info"""

    #Get Current User Info
    rows = db.execute("SELECT * FROM Employees WHERE EmployeeID = :id",
                         id=session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        #Check that the user entered his password
        if not request.form.get("password"):
            return empapology("Please Enter your password")

        #Check that the entered password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["Password"], request.form.get("password")):
            return empapology("Wrong password")

        #Check if he is changing his username
        if request.form.get("uname"):
            query = db.execute("SELECT * from Employees WHERE Username= :username", username=request.form.get("uname"))
            if len(query) != 0:
                return empapology("Username Already Exists")
            query = db.execute("UPDATE Employees SET Username= :username WHERE EmployeeID= :id",username=request.form.get("uname"), id=session["user_id"])
            return redirect("/Profile")

        #Check if he is changing his name
        if request.form.get("name") and request.form.get("name"):
            query = db.execute("UPDATE Employees SET Name = :name WHERE EmployeeID= :id",name=request.form.get("name"), id=session["user_id"])
            return redirect("/Profile")

        #Check if he is changing his password
        if request.form.get("newpassword") and request.form.get("confirmpassword"):
            if not (request.form.get("newpassword")==request.form.get("confirmpassword")):
                return empapology("password doesn't match")
            password = request.form.get("newpassword")
            hashed = generate_password_hash(password, method='sha256', salt_length=8)
            query = db.execute("UPDATE Employees SET Password= :password WHERE EmployeeID= :id",password=hashed, id=session["user_id"])
            return redirect("/Profile")
        
        return empapology("Please fill the whole form")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("empprofile.html", row=rows[0])





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return empapology(e.name)



#Manage The Store 
@app.route("/", methods=["GET", "POST"])
@login_required
def Management():
    """Edit User Info"""
    
    
    #Get Suppliers Data
    categories = db.execute("SELECT* FROM Categories order by CategoryName")
    suppliers = db.execute("SELECT * FROM Suppliers order by SupplierName")
    suplocations = db.execute("SELECT S.SupplierName,L.SupplierLocation FROM Suppliers as S, Supplier_Location as L WHERE S.SupplierID=L.SupplierID order by S.SupplierName,L.SupplierLocation")
    products = db.execute("SELECT * FROM Product order by ProductName")
    imports = db.execute("SELECT* FROM Product as P, Suppliers as S, Imports as I WHERE I.SupplierID = S.SupplierID and I.ProductID=P.ProductID order by S.SupplierName, P.ProductName, I.DateImported DESC")
    saleproducts = db.execute("SELECT P.ProductName, S.SalePercentage, S.SaleEndDate FROM Product as P, In_Sale_Products as S WHERE P.ProductID=S.ProductID")
    deliveries = db.execute("SELECT D.DeliveryID, T.TransactionID, C.FirstName, C.LastName, C.Address, T.TransactionDate, T.Price FROM Deliveries as D, Transactions as T, Customer as C WHERE D.TransactionID = T.TransactionID and T.IsDelivered=0 and C.CustomerID = T.CustomerID order by T.TransactionDate LIMIT 5")
    transproducts=[]
    for delivery in deliveries:
        transproducts.append(db.execute("SELECT T.TransactionID, P.ProductName, T.Quantity, T.BuyPrice FROM Product as P, Transaction_Contains_Products as T WHERE P.ProductID=T.ProductID and T.TransactionID = :tid",tid=delivery["TransactionID"]))
    
    #Define Password
    ManagementPassword="123456"

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("password"):
            return empapology("Please Enter Management password")

        #Check that the entered password is correct
        if  request.form.get("password") !=  ManagementPassword:
            return empapology("Wrong password")
        
        #Check If Insert Category
        if request.form.get("CatNameInsert") and request.form.get("CatURLInsert"):
            url=request.form.get("CatURLInsert")
            if not CheckIMAGEURL(url):
                return empapology("URL has to be ending with .jpg or .png")
            query = db.execute("INSERT INTO Categories (CategoryName,url) VALUES (:catname,:caturl)",catname=request.form.get("CatNameInsert"),caturl=request.form.get("CatURLInsert"))
            return redirect("/")

        #Update Category
        if request.form.get("selectCategoryEdit"):
            selectedCat = request.form.get("selectCategoryEdit")
            if request.form.get("CatURLEdit"):
                url=request.form.get("CatURLEdit")
                if not CheckIMAGEURL(url):
                    return empapology("URL has to be ending with .jpg or .png")
                query = db.execute("UPDATE Categories SET url = :url WHERE CategoryName = :selectedCat",selectedCat=selectedCat,url=request.form.get("CatURLEdit")) 
            if request.form.get("CatNameEdit"):
                query = db.execute("UPDATE Categories SET CategoryName = :catname WHERE CategoryName = :selectedCat",selectedCat=selectedCat,catname=request.form.get("CatNameEdit"))
            return redirect("/")
        
        #Delete Category
        if request.form.get("selectCategoryDelete"):
            query = db.execute("DELETE FROM Categories WHERE CategoryName = :selectedcat",selectedcat=request.form.get("selectCategoryDelete"))
            return redirect("/")
        
        #Insert Supplier 
        if request.form.get("SupplierNameInsert"):
            query=db.execute("INSERT INTO Suppliers (SupplierName) VALUES(:name)",name=request.form.get("SupplierNameInsert"))
            return redirect("/")
        
        #Insert Supplier Location
        if request.form.get("selectSupplierInsert") and request.form.get("SupplierLocInsert"):
            supname=request.form.get("selectSupplierInsert")
            suploc=request.form.get("SupplierLocInsert")
            supid = GetSupID(supname)
            query= db.execute("INSERT INTO Supplier_Location VALUES(:suploc, :supid)",suploc=suploc, supid=supid)
            return redirect("/")

        #Update Supplier Name
        if request.form.get("selectSupplierEdit") and request.form.get("SupplierNameEdit"):
            query = db.execute("UPDATE Suppliers SET SupplierName = :name WHERE SupplierName = :oldname", name=request.form.get("SupplierNameEdit"),oldname=request.form.get("selectSupplierEdit"))
            return redirect("/")
        
        #Update Supplier Location
        if request.form.get("selectSupLocEdit") and request.form.get("SupLocEdit"):
            text=request.form.get("selectSupLocEdit").split(", ")
            supname=text[0]
            suploc=text[1]
            supid = GetSupID(supname)
            query=db.execute("UPDATE Supplier_Location SET SupplierLocation= :newsuploc WHERE SupplierID= :supid and SupplierLocation= :suploc",suploc=suploc,supid=supid,newsuploc=request.form.get("SupLocEdit"))
            return redirect("/")

        #Delete Supplier
        if request.form.get("selectSupplierDelete"):
            query= db.execute("DELETE FROM Suppliers WHERE SupplierName= :supname", supname=request.form.get("selectSupplierDelete"))
            return redirect("/")

        
        #Delete Supplier Location
        if request.form.get("selectSupLocDelete"):
            text=request.form.get("selectSupLocDelete").split(", ")
            supname=text[0]
            suploc=text[1]
            supid = GetSupID(supname)
            query=db.execute("DELETE FROM Supplier_Location WHERE SupplierID= :supid and SupplierLocation= :suploc",supid=supid,suploc=suploc)
            return redirect("/")

        
        #Insert Product
        if CheckAllProductInsert():
            name = request.form.get("ProdNameInsert")
            desc = request.form.get("ProdDescInsert")
            price = request.form.get("ProdPriceInsert")
            url = request.form.get("ProdURLInsert")
            if not CheckIMAGEURL(url):
                return empapology("URL has to be ending with .jpg or .png")
            supname = request.form.get("ProdSupInsert") 
            supid = GetSupID(supname)
            catname = request.form.get("ProdCatInsert")
            catid = GetCatID(catname)
            quantity = 0
            query = db.execute("INSERT INTO Product (ProductName,ProductDescription,Price,Quantity,ImageURL,SupplierID,CategoryID) VALUES (:name,:desc,:price,:quantity,:url,:supid,:catid)",name=name,desc=desc,price=price,quantity=quantity,url=url,supid=supid,catid=catid)
            return redirect("/")

        #Edit Product 
        if request.form.get("SelectProdEdit"):
            prodname = request.form.get("SelectProdEdit")
            if request.form.get("ProdDescEdit"):
                query=db.execute("UPDATE Product SET ProductDescription= :desc WHERE ProductName= :prodname", desc=request.form.get("ProdDescEdit"), prodname=prodname)
            if request.form.get("ProdURLEdit"):
                url = request.form.get("ProdURLEdit")
                if not CheckIMAGEURL(url):
                    return empapology("URL has to be ending with .jpg or .png")
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
            return redirect("/")

        #Delete Product
        if request.form.get("SelectProdDelete"):
            query=db.execute("DELETE FROM Product WHERE ProductName= :name", name=request.form.get("SelectProdDelete"))
            return redirect("/")

        #ADD Import
        if request.form.get("ImportSupInsert") and request.form.get("ImportProdInsert") and request.form.get("ImportPriceInsert") and request.form.get("ImportQuanInsert") and request.form.get("ImportDateInsert"):
            supname=request.form.get("ImportSupInsert")
            prodname=request.form.get("ImportProdInsert")
            supid=GetSupID(supname)
            prodid=GetProdID(prodname)
            query = db.execute("SELECT SupplierID FROM Product WHERE ProductID=:prodid",prodid=prodid)
            if len(query) != 1:
                return empapology("Something Went Wrong")
            realsupid = query[0]["SupplierID"]
            if realsupid != supid:  #Preventing from Inserting if the supplier is different
                return empapology("This Product has a different Supplier")
            price = request.form.get("ImportPriceInsert")
            quantity = request.form.get("ImportQuanInsert")
            date = request.form.get("ImportDateInsert")
            query = db.execute("INSERT INTO Imports VALUES(:date, :supid, :prodid, :quantity, :price)",date=date,supid=supid,prodid=prodid,quantity=quantity,price=price)
            query = db.execute("UPDATE Product SET Quantity=Quantity+:quantity WHERE ProductID=:prodid",quantity=quantity,prodid=prodid)
            return redirect("/")
        
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
                return empapology("Something Wrong")
            quantity=query[0]["Quantity"]
            query=db.execute("SELECT Quantity FROM Product WHERE ProductID= :prodid",prodid=prodid)
            oldquantity=query[0]["Quantity"]
            newquantity = oldquantity - quantity
            if newquantity<0:
                return empapology("You can't delete this Import, not enough products")
            query = db.execute("UPDATE Product SET Quantity = :newquantity WHERE ProductID = :prodid", newquantity=newquantity, prodid=prodid)
            query = db.execute("DELETE FROM Imports WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",supid=supid,prodid=prodid,date=date)
            return redirect("/")

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
                return empapology("Something Wrong")
            oldquantity=query[0]["Quantity"]
            query=db.execute("SELECT Quantity FROM Product WHERE ProductID= :prodid",prodid=prodid)
            productquantity=query[0]["Quantity"]
            if request.form.get("ImportPriceEdit"):
                query=db.execute("UPDATE Imports SET Price= :price WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",price=request.form.get("ImportPriceEdit"),supid=supid,prodid=prodid,date=date)
            if request.form.get("ImportQuanEdit"):
                addedquantity=request.form.get("ImportQuanEdit")
                newquantity = productquantity - oldquantity + int(addedquantity)
                if newquantity < 0:
                    return empapology("Quantity isn't valid, not enough products")
                query = db.execute("UPDATE Product SET Quantity = :newquantity WHERE ProductID = :prodid", newquantity=newquantity, prodid=prodid)
                query=db.execute("UPDATE Imports SET Quantity= :quan WHERE SupplierID= :supid and ProductID= :prodid and DateImported= :date",quan=addedquantity,supid=supid,prodid=prodid,date=date)
            return redirect("/")

        # Sale Insert
        if request.form.get("SaleProdInsert") and request.form.get("SalePercentInsert") and request.form.get("SaleDateInsert"):
            prodname=request.form.get("SaleProdInsert")
            prodid = GetProdID(prodname)
            query = db.execute("SELECT * FROM In_Sale_Products WHERE ProductID = :prodid",prodid=prodid)
            if len(query) != 0:
                return empapology("This Product is already in Sale")
            query = db.execute("INSERT INTO In_Sale_Products VALUES(:percent,:date,:prodid)",percent=request.form.get("SalePercentInsert"),date=request.form.get("SaleDateInsert"),prodid=prodid)
            return redirect("/")

        #Sale Edit
        if request.form.get("SaleProdEdit"):
            prodname=request.form.get("SaleProdEdit")
            prodid = GetProdID(prodname)
            if request.form.get("SalePercentEdit"):
                query = db.execute("UPDATE In_Sale_Products SET SalePercentage=:percent WHERE ProductID= :prodid",percent=request.form.get("SalePercentEdit"),prodid=prodid)
            if request.form.get("SaleDateEdit"):
                query = db.execute("UPDATE In_Sale_Products SET SaleEndDate=:date WHERE ProductID= :prodid",date=request.form.get("SaleDateEdit"),prodid=prodid)
            return redirect("/")
        
        #Sale Delete
        if request.form.get("SaleProdDelete"):
            prodname=request.form.get("SaleProdDelete")
            prodid = GetProdID(prodname)
            query=db.execute("DELETE FROM In_Sale_Products WHERE ProductID= :prodid",prodid=prodid)
            return redirect("/")
        

        #POST WAS UNSUCCESFUL    
        return empapology("Something Missing")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("management.html", categories=categories,suppliers=suppliers,suplocations=suplocations,products=products, imports=imports, saleproducts=saleproducts, deliveries=deliveries, transproducts=transproducts)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)



def CheckAllProductInsert():
    if request.form.get("ProdNameInsert") and request.form.get("ProdDescInsert") and request.form.get("ProdPriceInsert") and request.form.get("ProdURLInsert") and request.form.get("ProdCatInsert") and request.form.get("ProdSupInsert"):
        return True 
    return False

def GetSupID (supname):
    query=db.execute("SELECT * FROM Suppliers WHERE SupplierName= :supname",supname=supname)
    if len(query) != 1:
        return empapology("Somthing Missing")
    supid=query[0]["SupplierID"]
    return supid

def GetCatID (catname):
    query=db.execute("SELECT * FROM Categories WHERE CategoryName= :catname",catname=catname)
    if len(query) != 1:
        return empapology("Somthing Missing")
    catid=query[0]["CategoryID"]
    return catid

def GetProdID (prodname):
    query=db.execute("SELECT * FROM Product WHERE ProductName= :prodname",prodname=prodname)
    if len(query) != 1:
        return empapology("Somthing Missing")
    prodid=query[0]["ProductID"]
    return prodid

