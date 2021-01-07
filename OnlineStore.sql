--
-- File generated with SQLiteStudio v3.2.1 on Fri Jan 8 00:17:19 2021
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Categories
CREATE TABLE Categories (CategoryID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, CategoryName STRING NOT NULL UNIQUE, url STRING);
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (1, 'Electronics', 'https://www.afcinternationalllc.com/wp-content/uploads/2016/07/AFC-Importing-Electronics-1-7-7-16-300x300.jpg');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (2, 'Home & Kitchen', 'https://b3h2.scene7.com/is/image/BedBathandBeyond/US-FW41-FY20-1206-1212-WEB-LP-Kitchen-C15-12-V3-10?$content$&wid=423');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (3, 'Food', 'https://d2ebzu6go672f3.cloudfront.net/media/content/images/cr/8c38e37d-e8b9-48dd-a9a8-65083a6115e5.jpg');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (4, 'Books', 'https://assets.readitforward.com/wp-content/uploads/2019/11/RIF-Q4-Books-We-Cant-Wait-To-Read-2020-RJD-1200x90011-12.jpg');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (5, 'Games & Toys', 'https://techcrunch.com/wp-content/uploads/2020/06/igor-karimov-M1nZU61xTK4-unsplash.jpg');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (6, 'Handmade', 'https://images-na.ssl-images-amazon.com/images/I/51idIpDP48L._AC_.jpg');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (7, 'Furniture', 'https://berkowitz.com.au/wp-content/uploads/2019/01/02_Charles_Sofa_Updated.jpg');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (8, 'Software', 'https://www.fingent.com/wp-content/uploads/2015/12/custom-software-development-01.png');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (9, 'Sports', 'https://media.socastsrm.com/wordpress/wp-content/blogs.dir/2626/files/2020/06/Sports-1.jpg');
INSERT INTO Categories (CategoryID, CategoryName, url) VALUES (10, 'Fashion', 'https://i.pinimg.com/originals/77/38/54/773854c17c415cd6eb1ccfefd78b898a.jpg');

-- Table: Customer
CREATE TABLE Customer (CustomerID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, Username VARCHAR (300) NOT NULL UNIQUE, Password VARCHAR (300) NOT NULL, FirstName VARCHAR (300) NOT NULL, LastName VARCHAR (300) NOT NULL, Address VARCHAR (500), PhoneNumber VARCHAR (20), RegisterationCode VARCHAR (30) UNIQUE, CodeShares INT, PromoCode VARCHAR (300), VoucherValue INT);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (2, 'Ammarovic', 'sha256$3wV9Gdf5$2514ddb2eb3b67d5725767eb43a07cc86f660fd98097d4edccfa19521dbb82d6', 'Ammar', 'Abdelmohsen', 'El Sheikh Zayed ', '01116185647', NULL, NULL, NULL, NULL);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (3, 'leomessi', 'sha256$RpM8e0HA$2e2620e1a09f5590d129ee353074876e0601f1735a46f1bcf07fc34ebf3cd8a3', 'Lionel', 'Messi', 'barcelona', '0999999', NULL, NULL, '6hUsiL', NULL);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (4, 'ronaldo7', 'sha256$Nem7bVM2$8d6df81287d9febca4474d68f287ae8e7a0ca8a8decdbfebb22c2fdf75def731', 'Cristiano', 'Ronaldo', 'Torino', '0777', NULL, NULL, NULL, NULL);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (5, 'ronaldoo', 'sha256$fNGXFFjt$f063129150574374c9f6bb7e38988d6eb8a72278aaf50bdd05dc1dc10797f8bd', 'Cristiano', 'Ronaldo', 'torinoo', '0777777', NULL, NULL, NULL, NULL);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (6, 'trika', 'sha256$AWGh0QVY$e7d6da9ccab532611837b259831cbde8ad5f27aadf69dd64a1a31a7d598d5008', 'Abou', 'Trika', 'qatar', '022222', 'T3Pgiw', NULL, NULL, 0);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (7, 'Becks', 'sha256$gURSEjZR$7cfe37359b68f30bae4e9c2b46525fdb905db3639698294bcf589e63508f5d89', 'David', 'Beckham', 'Manchester', '777777', 'RPPkJf', 10, NULL, 100);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (8, 'AhmedAyman', 'sha256$GvsIJP4p$d4dca046aa9311fc2a9b2252644f7c3f47a0d2906b462c4576ef00e9b2d66c2d', 'Ahmed', 'Ayman', '1 Elwarsha street abo elnomrus', '01147771061', 'l1fQ8y', 10, NULL, 0);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (9, 'Ammar', 'sha256$XqFoL6tQ$a4c1f8d0a935d642874f931d9517a9b3ca7e3648afe5791ce123b4ae6f395eeb', 'Ammar', 'Mohamed', 'hello', '01111111', '6hUsiL', 8, 'cWHcfA', 200);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (10, 'Rashy', 'sha256$u1LM2DKk$3aba5d4ac01696df7fd3bbe8d8359d8e74bdf34ac39e3c2287c7a3deb72fa0c1', 'Marcus', 'Rashford', 'Manchester', '01010101010', 'cWHcfA', 9, '6hUsiL', 250);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (11, 'OmarAhmed', 'sha256$lIYOuPbI$a8d5d41df155f883c64abdfd7ead88cb1e3c5008327dd4047892989f430555cb', 'omar', 'ahmed', '28 - elmostasmer elsagheer - elsheikh zayed - Giza - Egypt', '01100086995', 'noq9rQ', 10, NULL, 0);
INSERT INTO Customer (CustomerID, Username, Password, FirstName, LastName, Address, PhoneNumber, RegisterationCode, CodeShares, PromoCode, VoucherValue) VALUES (12, 'MohamedAkram', 'sha256$RScmCnJL$344d3ce637942333c2558fb6dc7ca44b9ebc0d2646aab3862181e0353a438ed2', 'Mohamed', 'Akram', 'Giza', '01032972946', 'eNrwkI', 10, NULL, 0);

-- Table: Customer_Cart
CREATE TABLE Customer_Cart (ProductID integer NOT NULL, CustomerID integer NOT NULL, Quantity double NOT NULL, PRIMARY KEY (ProductID, CustomerID), FOREIGN KEY (ProductID) REFERENCES Product ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (CustomerID) REFERENCES Customer (CustomerID) ON DELETE CASCADE ON UPDATE CASCADE);
INSERT INTO Customer_Cart (ProductID, CustomerID, Quantity) VALUES (1, 11, 1.0);
INSERT INTO Customer_Cart (ProductID, CustomerID, Quantity) VALUES (7, 11, 1.0);
INSERT INTO Customer_Cart (ProductID, CustomerID, Quantity) VALUES (6, 11, 1.0);
INSERT INTO Customer_Cart (ProductID, CustomerID, Quantity) VALUES (1, 12, 6.0);

-- Table: Customer_Rates_Products
CREATE TABLE Customer_Rates_Products (ProductID integer NOT NULL, CustomerID integer NOT NULL, Rating double NOT NULL, PRIMARY KEY (ProductID, CustomerID), FOREIGN KEY (ProductID) REFERENCES Product ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (CustomerID) REFERENCES Customer (CustomerID) ON DELETE NO ACTION ON UPDATE CASCADE);

-- Table: Customer_Wishlist
CREATE TABLE Customer_Wishlist (CustomerID INT NOT NULL REFERENCES Customer (CustomerID) ON DELETE CASCADE ON UPDATE CASCADE, ProductID INT REFERENCES Product ON DELETE CASCADE ON UPDATE CASCADE NOT NULL);

-- Table: Deliveries
CREATE TABLE Deliveries (DeliveryID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, DateDelivered DATETIME, TransactionID INT REFERENCES Transactions (TransactionID) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL);

-- Table: Imports
CREATE TABLE Imports (DateImported DATE NOT NULL UNIQUE, SupplierID INTEGER NOT NULL, ProductID INTEGER NOT NULL, Quantity DOUBLE NOT NULL, Price DOUBLE NOT NULL, PRIMARY KEY (DateImported, SupplierID, ProductID), FOREIGN KEY (SupplierID) REFERENCES Suppliers (SupplierID), FOREIGN KEY (ProductID) REFERENCES Product);

-- Table: In_Sale_Products
CREATE TABLE In_Sale_Products (SalePercentage double NOT NULL, Duration date NOT NULL, ProductID integer NOT NULL UNIQUE, PRIMARY KEY (ProductID), FOREIGN KEY (ProductID) REFERENCES Product ON DELETE CASCADE ON UPDATE CASCADE);
INSERT INTO In_Sale_Products (SalePercentage, Duration, ProductID) VALUES (0.1, 5, 1);

-- Table: Product
CREATE TABLE Product (ProductID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, ProductName VARCHAR (300) NOT NULL, ProductDescription VARCHAR (5000), Price DOUBLE NOT NULL, Quantity INT NOT NULL, InStock BOOLEAN, Rating INT CHECK (Rating > 0 and Rating < 6), ImageURL VARCHAR (1000), SupplierID INT NOT NULL REFERENCES Suppliers (SupplierID), CategoryID INT NOT NULL REFERENCES Categories (CategoryID) ON DELETE CASCADE ON UPDATE CASCADE);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (1, 'Samsung Note 8', 'About this item
6.3" Dual edge super AMOLED Quad HD+ display
64GB memory with removable Micro SD slot (up to 256GB), 6GB RAM
Water and dust resistant (IP68)
Dual 12MP rear cameras with OIS. 8MP front Camera with auto focus
Built in S-pen', 6000.0, 100, NULL, 3, 'https://cf5.s3.souqcdn.com/item/2017/12/14/23/87/92/30/item_XL_23879230_85741775.jpg', 1, 1);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (2, 'iPhone X', NULL, 10000.0, 10, NULL, NULL, 'https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcS5gamIRrLPBKtpN15kNGQH6mkYmjzZQo0dMeJwWJ3Eg13DyKkj2U1Zjtc_A33fnhTKPMm30eatNA&usqp=CAc', 2, 1);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (3, 'Braun MQ9087X MultiQuick 9', NULL, 2500.0, 30, NULL, NULL, 'https://cf5.s3.souqcdn.com/item/2018/02/26/23/58/80/40/item_XL_23588040_113044597.jpg', 3, 2);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (4, 'Philips HR7769', NULL, 4000.0, 40, NULL, NULL, 'https://cf5.s3.souqcdn.com/item/2016/10/23/78/94/04/6/item_XL_7894046_17033701.jpg', 4, 2);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (5, 'Molto XXL', NULL, 4.0, 500, NULL, NULL, 'https://mowfer.s3-eu-west-1.amazonaws.com/81569/339.jpg', 5, 3);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (6, 'Tiger', NULL, 3.0, 200, NULL, NULL, 'http://www.egyptfoodsgroup.com/uploads/productsMainImages/1581854986-tiger-sweet-chili-3d.png', 6, 3);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (7, '?????? ??????', NULL, 50.0, 100, NULL, NULL, 'https://storage.googleapis.com/rqiim-storage/5b436a1ef4e5e600113dd288.94e2ebb430516eccc1c0de58.jpeg', 7, 4);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (8, 'Handbook for Digital CMOS', NULL, 2000.0, 20, NULL, NULL, 'https://images.springer.com/sgw/books/medium/9783030371944.jpg', 8, 4);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (9, 'Xbox Series X', NULL, 16000.0, 100, NULL, NULL, 'https://media.wired.com/photos/5fa5dc3dba670daaf8e97a8d/master/pass/games_gear_series-x.jpg', 10, 5);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (10, 'Playstation 5', NULL, 20000.0, 100, NULL, NULL, 'https://www.nme.com/wp-content/uploads/2020/06/ps5-credit-sie@2000x1270.jpg', 11, 5);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (11, 'Marvel Iron Man toy', NULL, 100.0, 10, NULL, NULL, 'https://images-na.ssl-images-amazon.com/images/I/8144u3oYXwL._AC_SL1500_.jpg', 12, 5);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (12, 'Nintendo Wii', NULL, 3000.0, 50, NULL, NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Wii-console.jpg/1200px-Wii-console.jpg', 13, 5);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (13, 'Blue Scarf', NULL, 170.0, 10, NULL, NULL, 'https://scontent-hbe1-1.xx.fbcdn.net/v/t1.0-9/131394463_406448387469532_1808070698567647684_o.jpg?_nc_cat=107&ccb=2&_nc_sid=730e14&_nc_eui2=AeF_BY0LCTPJZBm3sxr_fnbZFC658cedlGcULrnxx52UZxPxtZuBjzvcuQ_6rlQdhg-krStI1cmz8kHybdwSMmJb&_nc_ohc=P5vwbMhbUVcAX_dfcoe&_nc_ht=scontent-hbe1-1.xx&oh=ef671bdc20c2b6028fe229c7b1e62a29&oe=60094757', 14, 6);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (14, 'Black Bed', NULL, 2000.0, 5, NULL, NULL, 'https://www.ikea.com/us/en/images/products/malm-high-bed-frame-2-storage-boxes-black-brown-luroey__0637597_PE698414_S5.JPG?f=s', 16, 7);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (15, 'Adobe Photoshop', NULL, 1000.0, 10, NULL, NULL, 'https://images.indianexpress.com/2020/11/Adobe-Photoshop-CC-1.jpg', 17, 8);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (16, 'Manchester United 2020/2021 Home Season', NULL, 500.0, 100, NULL, NULL, 'https://images.sportsdirect.com/images/products/37717608_l.jpg', 18, 9);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (17, 'Nike Mercurial', NULL, 4000.0, 100, NULL, NULL, 'https://images.sportsdirect.com/images/products/20101108_l.jpg', 19, 9);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (18, 'Black Cotton T-shirt', NULL, 200.0, 200, NULL, NULL, 'https://lp2.hm.com/hmgoepprod?set=quality%5B79%5D%2Csource%5B%2Ff5%2Fc4%2Ff5c4939114fcc731acfada4ebb68f1da42cad909.jpg%5D%2Corigin%5Bdam%5D%2Ccategory%5Bmen_tshirtstanks_shortsleeve%5D%2Ctype%5BDESCRIPTIVESTILLLIFE%5D%2Cres%5Bm%5D%2Chmver%5B1%5D&call=url[file:/product/main]', 20, 10);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (19, 'Timberland T-shirt', NULL, 199.0, 200, NULL, NULL, 'https://s3.gsxtr.com/i/pr/t-shirt-timberland-yc-stack-logo-t-shirt-black-white-261301-450-1.jpg', 22, 10);
INSERT INTO Product (ProductID, ProductName, ProductDescription, Price, Quantity, InStock, Rating, ImageURL, SupplierID, CategoryID) VALUES (20, 'Zara Trousers', NULL, 320.0, 10, NULL, NULL, 'https://4.imimg.com/data4/UO/JO/ANDROID-47109325/product-500x500.jpeg', 23, 10);

-- Table: RefundProducts
CREATE TABLE RefundProducts (RefundID INT, ProductID INT, Quantity INT, PRIMARY KEY (RefundID, ProductID), FOREIGN KEY (RefundID) REFERENCES Refunds (RefundID) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (ProductID) REFERENCES Product ON DELETE NO ACTION ON UPDATE NO ACTION);

-- Table: Refunds
CREATE TABLE Refunds (RefundID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, Price DOUBLE NOT NULL, DateRefunded DATETIME, TransactionID INT REFERENCES Transactions (TransactionID) ON DELETE RESTRICT ON UPDATE NO ACTION NOT NULL);

-- Table: Supplier_Location
CREATE TABLE Supplier_Location (SupplierLocation STRING NOT NULL, SupplierID INT REFERENCES Suppliers (SupplierID) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL, PRIMARY KEY (SupplierLocation, SupplierID));
INSERT INTO Supplier_Location (SupplierLocation, SupplierID) VALUES ('Japan', 1);
INSERT INTO Supplier_Location (SupplierLocation, SupplierID) VALUES ('China', 1);
INSERT INTO Supplier_Location (SupplierLocation, SupplierID) VALUES ('Egypt', 2);
INSERT INTO Supplier_Location (SupplierLocation, SupplierID) VALUES ('Giza', 2);

-- Table: Suppliers
CREATE TABLE Suppliers (SupplierID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, SupplierName STRING NOT NULL);
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (1, 'Samsung');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (2, 'Apple');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (3, 'Braun');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (4, 'Philips');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (5, 'Edita');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (6, 'Egypt Foods');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (7, 'Dar El Shorook');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (8, 'Springer');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (9, 'Nahder Misr');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (10, 'Microsoft');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (11, 'Sony');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (12, 'Marvel');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (13, 'Nintendo');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (14, 'Hookwarts');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (15, 'Ahmed Ayman');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (16, 'Ikea');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (17, 'Adobe');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (18, 'Adidas');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (19, 'Nike');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (20, 'H&M');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (21, 'La Coste');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (22, 'Timberland');
INSERT INTO Suppliers (SupplierID, SupplierName) VALUES (23, 'Zara');

-- Table: Transaction_Contains_Products
CREATE TABLE Transaction_Contains_Products (TransactionID INT NOT NULL, ProductID INT NOT NULL, Quantity INT NOT NULL, PRIMARY KEY (TransactionID, ProductID), FOREIGN KEY (TransactionID) REFERENCES Transactions (TransactionID) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (ProductID) REFERENCES Product ON DELETE NO ACTION ON UPDATE NO ACTION);
INSERT INTO Transaction_Contains_Products (TransactionID, ProductID, Quantity) VALUES (1, 8, 1);
INSERT INTO Transaction_Contains_Products (TransactionID, ProductID, Quantity) VALUES (1, 1, 1);
INSERT INTO Transaction_Contains_Products (TransactionID, ProductID, Quantity) VALUES (1, 3, 5);
INSERT INTO Transaction_Contains_Products (TransactionID, ProductID, Quantity) VALUES (2, 5, 2);
INSERT INTO Transaction_Contains_Products (TransactionID, ProductID, Quantity) VALUES (3, 7, 1);
INSERT INTO Transaction_Contains_Products (TransactionID, ProductID, Quantity) VALUES (3, 9, 1);

-- Table: Transactions
CREATE TABLE Transactions (TransactionID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, TransactionDate DATETIME, IsDelivered BOOLEAN, Price DOUBLE NOT NULL, PaymentMethod VARCHAR (100), CustomerID INT REFERENCES Customer (CustomerID) ON DELETE NO ACTION ON UPDATE CASCADE NOT NULL);
INSERT INTO Transactions (TransactionID, TransactionDate, IsDelivered, Price, PaymentMethod, CustomerID) VALUES (1, '1/4/2000', 1, 15000.0, 'Cash', 8);
INSERT INTO Transactions (TransactionID, TransactionDate, IsDelivered, Price, PaymentMethod, CustomerID) VALUES (2, '1/4/2000', 1, 15000.0, 'Cash', 8);
INSERT INTO Transactions (TransactionID, TransactionDate, IsDelivered, Price, PaymentMethod, CustomerID) VALUES (3, '1/4/2000', 1, 15000.0, 'Cash', 8);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
