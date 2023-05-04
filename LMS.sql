-- Task 1: Create the following tables for the LMS database.
-- PUBLISHER: Publisher_Name, Phone, Address

CREATE TABLE PUBLISHER (
    Publisher_Name VARCHAR(75) NOT NULL, 
    Phone VARCHAR(13) NOT NULL, 
    Address VARCHAR(150) NOT NULL, 
    PRIMARY KEY (Publisher_Name)
);

-- LIBRARY_BRANCH: Branch_Id, Branch_Name, Branch_Address

CREATE TABLE LIBRARY_BRANCH (
    Branch_Id INTEGER NOT NULL, 
    Branch_Name VARCHAR(75) NOT NULL, 
    Branch_Address VARCHAR(150) NOT NULL, 
    PRIMARY KEY (Branch_Id)
);

-- BORROWER: Card_No, Name, Address, Phone

CREATE TABLE BORROWER (
    Card_No INTEGER PRIMARY KEY, 
    Name VARCHAR(75) NOT NULL, 
    Address VARCHAR(150) NOT NULL, 
    Phone VARCHAR(13) NOT NULL
);

-- BOOK: Book_Id, Title, Publisher_name

CREATE TABLE BOOK (
    Book_Id INTEGER NOT NULL, 
    Title VARCHAR(75) NOT NULL, 
    Publisher_name VARCHAR(75),  
    PRIMARY KEY (Book_Id),
    FOREIGN KEY (Publisher_name) REFERENCES PUBLISHER(Publisher_Name)
);

-- BOOK_LOANS: Book_Id, Branch_Id, Card_No, Date_Out, Due_Date, Returned_date
-- Assume user can checkout multiple same book from one branch at one time (no primary key in attributes alone)

CREATE TABLE BOOK_LOANS (
    Book_Id INT NOT NULL,     
    Branch_Id INT NOT NULL, 
    Card_No INT NOT NULL, 
    Date_Out DATETIME NOT NULL, 
    Due_Date DATETIME NOT NULL, 
    Returned_date DATETIME, 
    FOREIGN KEY(Book_Id) REFERENCES BOOK(Book_Id),
    FOREIGN KEY(Branch_Id) REFERENCES LIBRARY_BRANCH(Branch_Id),
    FOREIGN KEY(Card_No) REFERENCES BORROWER(Card_No)
);

-- BOOK_COPIES: Book_Id, Branch_Id, No_Of_Copies

CREATE TABLE BOOK_COPIES (
    Book_Id INT NOT NULL, 
    Branch_Id INT NOT NULL, 
    No_Of_Copies INT NOT NULL, 
    FOREIGN KEY(Book_Id) REFERENCES BOOK(Book_Id),
    FOREIGN KEY(Branch_Id) REFERENCES LIBRARY_BRANCH(Branch_Id)
);

-- BOOK_AUTHORS: Book_Id, Author_Name
CREATE TABLE BOOK_AUTHORS (
    Book_Id INTEGER NOT NULL, 
    Author_Name VARCHAR(50) NOT NULL, 
    PRIMARY KEY (Book_Id),
    FOREIGN KEY(Book_Id) REFERENCES BOOK(Book_Id)
);

.mode csv
.import --skip 1 Book_Authors.csv BOOK_AUTHORS
.import --skip 1 Book_Copies.csv BOOK_COPIES
.import --skip 1 Book_Loans.csv BOOK_LOANS
.import --skip 1 Book.csv BOOK
.import --skip 1 Borrower.csv BORROWER
.import --skip 1 Library_Branch.csv LIBRARY_BRANCH
.import --skip 1 Publisher.csv PUBLISHER

-- Added Trigger to Table afterwards to preserve the previous data.
CREATE TRIGGER return_date_trigger 
   BEFORE INSERT ON BOOK_LOANS
BEGIN
   SELECT
        CASE WHEN NEW.Returned_date < NEW.Date_Out THEN
   	        RAISE (ABORT, "Returned Date is before Check Out Date. Please Correct Issue.")
        END;
END;

.mode table
.header on

-- After inserting the data run a query to calculate the total number of records per table.
SELECT (SELECT count(*) FROM BOOK_AUTHORS) "Book Authors Table Amount", (SELECT count(*) FROM BOOK_COPIES) "Book Copies Table Amount", (SELECT count(*) FROM BOOK_LOANS) "Book Loans Table Amount", (SELECT count(*) FROM BOOK) "Book Table Amount", (SELECT count(*) FROM BORROWER) "Borrower Table Amount", (SELECT count(*) FROM LIBRARY_BRANCH) "Library Branch Table Amount", (SELECT count(*) FROM PUBLISHER) "Publisher Table Amount";


-- -- -- Question 1: Insert yourself as a New Borrower. Do not provide the Card_no in your query. [2 points]
-- INSERT INTO BORROWER(Name, Address, Phone) VALUES ('Kyle Henry', "1234 Druery Ln", "123-456-7890");

-- -- -- Question 2: Update your phone number to (837) 721-8965 [2 points]
-- UPDATE BORROWER SET Phone='837-721-8965' WHERE Name='Kyle Henry' AND Address='1234 Druery Ln' AND Phone='123-456-7890';

-- -- -- Question 3: Increase the number of book_copies by 1 for the ‘East Branch’ [2 points]
-- UPDATE BOOK_COPIES SET No_Of_Copies=No_Of_Copies + 1 WHERE Branch_Id IN (SELECT Branch_Id FROM LIBRARY_BRANCH WHERE Branch_Name='East Branch');

-- -- -- Question 4-a: Insert a new BOOK with the following info: Title: ‘Harry Potter and the Sorcerer's Stone’ ; Book_author: ‘J.K. Rowling’ 
-- INSERT INTO BOOK(Title) VALUES ("Harry Potter and the Sorcerer's Stone");
-- INSERT INTO BOOK_AUTHORS VALUES (last_insert_rowid(), "J.K. Rowling");

-- -- -- Question 4-b: You also need to insert the following branches:
-- INSERT INTO LIBRARY_BRANCH(Branch_Name, Branch_Address) VALUES ('North Branch', "456 NW, Irving, TX 76100");
-- INSERT INTO LIBRARY_BRANCH(Branch_Name, Branch_Address) VALUES ('UTA Branch', " 123 Cooper St, Arlington TX 76101");

-- -- -- Question 5: Return all Books that were loaned between March 5, 2022 until March 23, 2022. List Book title and Branch name, and how many days it was borrowed for. [10 points]
-- SELECT Title, Branch_Name, julianday(Returned_date) - julianday(Date_Out) "Days Borrowed" FROM (BOOK NATURAL JOIN LIBRARY_BRANCH) NATURAL JOIN BOOK_LOANS WHERE Date_Out BETWEEN "2022-03-05" AND "2022-03-23";

-- -- -- Question 6: Return a List borrower names, that have books not returned. [3 points]
-- SELECT Name FROM BORROWER NATURAL JOIN BOOK_LOANS WHERE Returned_date IS NULL;

-- -- -- Question 7: Create a report that will return all branches with the number of books borrowed per branch separated by if they have been returned, still borrowed, or late.
-- CREATE VIEW BORROWER_REPORT AS SELECT Branch_Id, SUM(CASE WHEN Returned_date IS NOT NULL THEN 1 ELSE 0 END) "Books Returned", SUM(CASE WHEN Returned_date IS NULL THEN 1 ELSE 0 END) "Books Still Borrowed", SUM(CASE WHEN Returned_date > Due_Date THEN 1 ELSE 0 END) "Books Late" FROM BOOK_LOANS GROUP BY Branch_Id;

-- -- -- Question 8: What is the maximum number of days a book has been borrowed. [2 points]
-- SELECT MAX(julianday(Returned_date) - julianday(Date_Out)) "Max Days Borrowed" FROM BOOK_LOANS;

-- -- -- Question 9: Create a report for Ethan Martinez with all the books they borrowed. List the book title and author. Also, calculate the number of days each book was borrowed for and if any book is late in return date. Order the results by the date_out.
-- CREATE VIEW ETHAN_MARTINEZ_REPORT AS SELECT Title, Author_Name, julianday(Returned_date) - julianday(Date_Out) "Days Borrowed", CASE WHEN Returned_date > Due_Date THEN "Late" ELSE "Not Late" END "Book Returned Late" FROM (((BORROWER NATURAL JOIN BOOK_LOANS) NATURAL JOIN BOOK) NATURAL JOIN BOOK_AUTHORS) WHERE Name='Ethan Martinez' ORDER BY Date_Out ASC;

-- -- -- Question 10: Return all borrowers and their addresses that borrowed a book. [3 points]
-- SELECT DISTINCT Name, Address FROM BORROWER NATURAL JOIN BOOK_LOANS;


-- PART 3

-- Add an extra column ‘Late’ to the Book_Loan table. Values will be 0-for non-late retuns, and 1-for late returns. Then update the ‘Late’ column with '1' for all records that they have a return date later than the due date and with '0' for those were returned on time.
ALTER TABLE BOOK_LOANS ADD Late INTEGER;
UPDATE BOOK_LOANS SET Late = CASE WHEN Returned_date <= Due_Date THEN 0 ELSE 1 END;


-- Add an extra column ‘LateFee’ to the Library_Branch table, decide late fee per day for each branch and update that column.
ALTER TABLE LIBRARY_BRANCH ADD LateFee FLOAT;
UPDATE LIBRARY_BRANCH SET LateFee = CASE WHEN Branch_Id = 1 THEN 0.5 WHEN Branch_Id = 2 THEN 1 WHEN Branch_Id = 3 THEN 1.75 END;


-- Create a view vBookLoanInfo that retrieves all information per book loan. The view should have the
-- following attributes:
-- • Card_No,
-- • Borrower Name
-- • Date_Out,
-- • Due_Date,
-- • Returned_date
-- • Total Days of book loaned out as 'TotalDays'– you need to change weeks to days
-- • Book Title
-- • Number of days later return – if returned before or on due_date place zero
-- • Branch ID
-- • Total Late Fee Balance 'LateFeeBalance' – If the book was not retuned late than fee = ‘0’

CREATE VIEW vBookLoanInfo AS 
    SELECT Card_No, 
    Name "Borrower Name", 
    Date_Out, Due_Date, 
    Returned_date, 
    julianday(Returned_date) - julianday(Date_Out) "Days Borrowed", 
    Title "Book Title", 
    CASE 
        WHEN Late = 0 OR Late IS NULL
        THEN 0 
        ELSE julianday(Returned_date) - julianday(Due_Date) 
    END "Number Days Late",
    Branch_Id "Branch ID",
    CASE 
        WHEN Late = 0 OR Late IS NULL
        THEN 0
        ELSE (julianday(Returned_date) - julianday(Due_Date)) * LateFee
    END "LateFeeBalance"
    FROM ((BOOK_LOANS NATURAL JOIN LIBRARY_BRANCH) NATURAL JOIN BORROWER) NATURAL JOIN BOOK;
