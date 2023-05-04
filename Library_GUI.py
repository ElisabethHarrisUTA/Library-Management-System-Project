import sqlite3
from tkinter import *
import tkinter.messagebox
import tksheet
from tkcalendar import Calendar
from tkinter import ttk
from datetime import datetime


#create a tk window
root = Tk()

root.title('Library Database Management System')
root.geometry("600x800")

cob_book_list = []

# Function for checking the
# key pressed and updating
# the listbox
def cob_check_key(event, lb):
    value = event.widget.get()
    print(cob_book_list)
      
    # get data from l
    if value == '':
        data = cob_book_list
    else:
        data = []
        for item in cob_book_list:
            if value.lower() in item.lower():
                data.append(item)
   
    # clear previous data
    lb.delete(0, 'end')
   
    # put new data
    for item in data:
        lb.insert('end', item)

def update_book_list(branch):
    update = sqlite3.connect('LMS.db')
    update_cur = update.cursor()
    update_cur.execute("SELECT Title FROM (LIBRARY_BRANCH NATURAL JOIN BOOK_COPIES) NATURAL JOIN BOOK WHERE Branch_Name = :name AND No_Of_Copies > 0", {'name' : branch})
    global cob_book_list
    cob_book_list = []

    for row in update_cur:
        for field in row:
            cob_book_list.append(field)
    print(cob_book_list)
    update.commit()
    update.close()

# Check Out Book Window
def open_cob_window():
    cob = sqlite3.connect('LMS.db')
    cob_cur = cob.cursor()
    cob_window = Toplevel(root)
    cob_window.title("Check Out Book Window")
    cob_window.geometry("800x500")
    cob_window.resizable(FALSE,FALSE)
 
    title_label = Label(cob_window, text = 'Check Out Book', justify='center', font=("Arial", 20))
    title_label.place(relx=0.5, rely=0.05, anchor=CENTER)
    
    borrower_no_label = Label(cob_window, text = 'Borrower Number', font=("Arial", 13))
    borrower_no_label.place(relx=0.2, rely=0.2)
    
    borrower_no = Entry(cob_window, width = 30, font=("Arial", 13))
    borrower_no.place(relx=0.38, rely=0.2)

    branches_label = Label(cob_window, text = 'Library Branch', font=("Arial", 13))
    branches_label.place(relx=0.2, rely=0.27)

    cob_cur.execute("SELECT Branch_Name FROM LIBRARY_BRANCH")
    options = []
    for row in cob_cur:
        for field in row:
            options.append(field)

    book = Entry(cob_window, width = 30, font=("Arial", 13))
    book.place(relx=0.38, rely=0.34)

    book_list_lb = Listbox(cob_window, width=27)
    book_list_lb.place(relx=0.385, rely=0.39)

    book.bind("<KeyRelease>", lambda event: (cob_check_key(event, lb=book_list_lb)))

    # datatype of menu text
    clicked = StringVar()
    clicked.set( "Select" )
    branches = OptionMenu(cob_window , clicked , *options, command=lambda event: (update_book_list(clicked.get())))
    branches.place(relx=0.38, rely=0.27)

    book_name_label = Label(cob_window, text = 'Book Name', font=("Arial", 13))
    book_name_label.place(relx=0.2, rely=0.34)

    submit_button = Button(cob_window, text = 'Check Out Book', width=20, height = 2, font=("Arial", 15), command=lambda : on_cob_sumbit(borrower_no.get(), clicked.get(), book.get()))
    submit_button.place(relx=0.5, rely=0.9, anchor=CENTER)
    cob.commit()
    cob.close()

def on_cob_sumbit(card_no, branch, book):
    submit = sqlite3.connect('LMS.db')
    submit_cur = submit.cursor()
    try:
        submit_cur.execute("INSERT INTO BOOK_LOANS (Book_Id, Branch_Id, Card_No, Date_Out, Due_Date) VALUES ((SELECT Book_Id FROM (BOOK NATURAL JOIN BOOK_COPIES) NATURAL JOIN LIBRARY_BRANCH WHERE Title = :title AND Branch_Name = :name AND No_Of_Copies > 0), (SELECT Branch_Id FROM LIBRARY_BRANCH WHERE Branch_Name = :name), (SELECT Card_No FROM BORROWER WHERE Card_No = :card), date('now'), date('now', '+1 month'))", {'title' : book, 'name' : branch, 'card' : card_no})
        submit_cur.execute("UPDATE BOOK_COPIES SET No_Of_Copies = No_of_Copies - 1 WHERE Branch_Id = (SELECT Branch_Id FROM LIBRARY_BRANCH WHERE Branch_Name = :name) AND Book_Id = (SELECT Book_Id FROM BOOK WHERE Title = :title)", {'name' : branch, 'title' : book})
        submit_cur.execute("SELECT Book_Id, Branch_Id, No_Of_Copies FROM (BOOK_COPIES NATURAL JOIN LIBRARY_BRANCH) NATURAL JOIN BOOK WHERE Branch_Name = :name AND Title = :title", {'name' : branch, 'title' : book})
        copies = submit_cur.fetchall()
        print_copies = 'Updated Book_Copies Entry: '
        for copy in copies:
            print_copies +=  "There are " + str(copy[2]) + " copies of " + book + " left at " + branch + ".\n Output of query(" + str(copy[0]) + " " + str(copy[1]) + " " + str(copy[2]) + ")"

        tkinter.messagebox.showinfo("Information",  message= print_copies)
    except sqlite3.Error as err:
        print(err.args)
        if "BOOK_LOANS.Book_Id" in err.args[0]:
            tkinter.messagebox.showerror("Fix Book Title!", "Error. Please input a Book Title that is available at the selected branch.")
        elif "BOOK_LOANS.Card_No" in err.args[0]:
            tkinter.messagebox.showerror("Fix Card Number!", "Error. Please input an existing card number.")
        elif "BOOK_LOANS.Branch_Id" in err.args[0]:
            tkinter.messagebox.showerror("Fix Branch Name!", "Error. Please input an existing Branch Name.")
        else:
            tkinter.messagebox.showerror("Unknown Error!", "An unidentified error has occured. Please contact your IT department.")

    submit.commit()
    submit.close()

# Add Borrower Window
def open_borrower_window():
    borrower_window = Toplevel(root)
    borrower_window.title("Add Borrower Window")
    borrower_window.geometry("800x500")
    borrower_window.resizable(FALSE,FALSE)
    
    title_label = Label(borrower_window, text = 'Add Borrower', justify='center', font=("Arial", 20))
    title_label.place(relx=0.5, rely=0.05, anchor=CENTER)

    borrower_name_label = Label(borrower_window, text = 'Borrower Name', font=("Arial", 13))
    borrower_name_label.place(relx=0.2, rely=0.2)
    
    borrower_name = Entry(borrower_window, width = 30, font=("Arial", 13))
    borrower_name.place(relx=0.40, rely=0.2)

    borrower_address_label = Label(borrower_window, text = 'Borrower Address', font=("Arial", 13))
    borrower_address_label.place(relx=0.2, rely=0.27)

    borrower_address = Entry(borrower_window, width = 30, font=("Arial", 13))
    borrower_address.place(relx=0.40, rely=0.27)

    borrower_phone_no_label = Label(borrower_window, text = 'Borrower Phone No.', font=("Arial", 13))
    borrower_phone_no_label.place(relx=0.2, rely=0.34)

    borrower_phone_no = Entry(borrower_window, width = 30, font=("Arial", 13))
    borrower_phone_no.place(relx=0.40, rely=0.34)

    submit_button = Button(borrower_window, text = 'Add Borrower', width=20, height = 2, font=("Arial", 15), command=lambda : on_borrower_sumbit(borrower_name.get(), borrower_address.get(), borrower_phone_no.get()))
    submit_button.place(relx=0.5, rely=0.9, anchor=CENTER)

def on_borrower_sumbit(name, address, phone):
    if name == '':
        tkinter.messagebox.showerror("Enter a Name!", "The borrower needs to have a name!")
        return
    elif address == '':
        tkinter.messagebox.showerror("Enter an Address!", "The borrower needs to have an address!")
        return
    elif phone == '':
        tkinter.messagebox.showerror("Enter a Phone Number!", "The borrower needs to have a Phone Number!")
        return
    
    submit = sqlite3.connect('LMS.db')
    borrower_submit = submit.cursor()
    try:
        borrower_submit.execute("INSERT INTO BORROWER (Name, Address, Phone) VALUES (:borrower, :address, :phone_no)", {'borrower' : name, 'address' : address, 'phone_no' : phone})
        borrower_submit.execute("SELECT Card_No FROM BORROWER WHERE Name = :name AND Address = :address AND Phone = :phone",{'name' : name, 'address' : address, 'phone' : phone})
        card = borrower_submit.fetchall()
        print_card = ""
        for cards in card:
            print_card += "Your library card number is " + str(cards[0])
        tkinter.messagebox.showinfo("Information",  message= print_card)
    except sqlite3.Error as err:
        tkinter.messagebox.showerror("Unknown Error!", "An unidentified error has occured. Please contact your IT department.")

    submit.commit()
    submit.close()

# Add New Book Window
def open_add_book_window():
    book = sqlite3.connect('LMS.db')
    book_cur = book.cursor()
    add_book_window = Toplevel(root)
    add_book_window.title("Add New Book Window")
    add_book_window.geometry("800x500")
    add_book_window.resizable(FALSE,FALSE)
 
    title_label = Label(add_book_window, text = 'Add New Book', justify='center', font=("Arial", 20))
    title_label.place(relx=0.5, rely=0.05, anchor=CENTER)

    book_title_label = Label(add_book_window, text = 'Book Title', font=("Arial", 13))
    book_title_label.place(relx=0.2, rely=0.2)
    
    book_title = Entry(add_book_window, width = 30, font=("Arial", 13))
    book_title.place(relx=0.40, rely=0.2)

    book_publisher_label = Label(add_book_window, text = 'Book Publisher', font=("Arial", 13))
    book_publisher_label.place(relx=0.2, rely=0.27)

    book_cur.execute("SELECT Publisher_Name FROM PUBLISHER")
    options = []
    for row in book_cur:
        for field in row:
            options.append(field)

    # datatype of menu text
    clicked = StringVar()
    clicked.set( "Select" )
    book_publisher = OptionMenu(add_book_window , clicked , *options)
    book_publisher.place(relx=0.4, rely=0.27)

    book_author_label = Label(add_book_window, text = 'Book Author', font=("Arial", 13))
    book_author_label.place(relx=0.2, rely=0.34)

    book_author = Entry(add_book_window, width = 30, font=("Arial", 13))
    book_author.place(relx=0.40, rely=0.34)

    submit_button = Button(add_book_window, text = 'Add Book', width=20, height = 2, font=("Arial", 15), command=lambda : on_add_book_sumbit(book_title.get(), clicked.get(), book_author.get()))
    submit_button.place(relx=0.5, rely=0.9, anchor=CENTER)

    book.commit()
    book.close()

def on_add_book_sumbit(book, publisher, author):
    if book == '':
        tkinter.messagebox.showerror("Enter a Book Title!", "The book needs to have a title!")
        return
    elif publisher == 'Select':
        tkinter.messagebox.showerror("Select a Publisher!", "The book needs to have a publisher!")
        return
    elif author == '':
        tkinter.messagebox.showerror("Enter an Author!", "The book needs to have an author!")
        return
    
    submit = sqlite3.connect('LMS.db')
    book_submit = submit.cursor()
    try:
        book_submit.execute("INSERT INTO BOOK (Title, Publisher_name) VALUES (:title, :name)", {'title' : book, 'name' : publisher})
        book_submit.execute("INSERT INTO BOOK_AUTHORS VALUES ((SELECT Book_Id FROM BOOK WHERE Title = :title), :author)", {'title' : book, 'author' : author})
        book_submit.execute("SELECT Branch_Id FROM LIBRARY_BRANCH")
        branches = book_submit.fetchall()
        for branch in branches:
            book_submit.execute("INSERT INTO BOOK_COPIES VALUES ((SELECT Book_Id FROM BOOK WHERE Title = :title), :branch, 5)", {'title' : book, 'branch' : branch[0]})
        tkinter.messagebox.showinfo("Information",  "Added new book successfully!")
    except sqlite3.Error as err:
        if 'UNIQUE' in err.args[0]:
            tkinter.messagebox.showerror("Book & Author already Used!", "This combination of book title & author already exists in the table!")
        else:
            print(err.args[0])
            tkinter.messagebox.showerror("Unknown Error!", "An unidentified error has occured. Please contact your IT department.")
    
    submit.commit()
    submit.close()

def update_copies_info_list(list_tb, book, copy_list):
    list = sqlite3.connect('LMS.db')
    list_cur = list.cursor()
    list_cur.execute("SELECT Branch_Name, COUNT(*) FROM (BOOK_LOANS NATURAL JOIN LIBRARY_BRANCH) NATURAL JOIN BOOK WHERE Title = :title", {'title' : book})
    copy_list = list_cur.fetchall()

    list_tb.set_sheet_data(copy_list)

    list.commit()
    list.close()

# List Copies Lo Window
def open_copies_window():
    copy = sqlite3.connect('LMS.db')
    copy_cur = copy.cursor()

    copies_window = Toplevel(root)
    copies_window.title("List Copies Loaned Window")
    copies_window.geometry("800x700")
    copies_window.resizable(FALSE,FALSE)
 
    title_label = Label(copies_window, text = 'List Copies Loaned', justify='center', font=("Arial", 20))
    title_label.place(relx=0.5, rely=0.05, anchor=CENTER)


    copies_info_list = []
    copies_info_list_tb = tksheet.Sheet(copies_window, header=["Branch Title", "Copies Loaned"], width=400, height = 400)
    copies_info_list_tb.grid()
    copies_info_list_tb.place(relx=0.385, rely=0.27)
    copies_info_list_tb.set_sheet_data(copies_info_list)

    
    book_publisher_label = Label(copies_window, text = 'Book', font=("Arial", 13))
    book_publisher_label.place(relx=0.2, rely=0.20)

    # datatype of menu text
    copy_cur.execute("SELECT Title FROM BOOK")
    book_list = []
    for row in copy_cur:
        for field in row:
            book_list.append(field)
    clicked = StringVar()
    clicked.set( "Select" )
    book_publisher = OptionMenu(copies_window , clicked , *book_list, command=(lambda event: (update_copies_info_list(copies_info_list_tb, clicked.get(),copies_info_list))))
    book_publisher.place(relx=0.4, rely=0.20)

def update_book_loan_info_list(list_tb, start_date, end_date, info_list):
    list = sqlite3.connect('LMS.db')
    list_cur = list.cursor()
    date_format = '%m/%d/%y'
    dt = datetime.strptime(start_date, date_format)
    start = dt.strftime("%Y-%m-%d")
    dts = datetime.strptime(end_date, date_format)
    end = dts.strftime("%Y-%m-%d")
    list_cur.execute("SELECT Card_No, Title, Branch_Name, julianday(Returned_Date) - julianday(Due_Date) FROM (BOOK_LOANS NATURAL JOIN LIBRARY_BRANCH) NATURAL JOIN BOOK WHERE Returned_Date > Due_Date AND Due_Date BETWEEN :start AND :end", {'start' : start, 'end' :end})
    info_list = list_cur.fetchall()
    print(info_list)


    list_tb.set_sheet_data(info_list)
    list.commit()
    list.close()

# Check Out Book Window
def open_late_window():
    late_window = Toplevel(root)
    late_window.title("Late Books Window")
    late_window.geometry("1200x650")
    late_window.resizable(FALSE,FALSE)
 
    title_label = Label(late_window, text = 'Late Books', justify='center', font=("Arial", 20))
    title_label.place(relx=0.5, rely=0.05, anchor=CENTER)

    start_date_label = Label(late_window, text = 'Start Date', font=("Arial", 13))
    start_date_label.place(relx=0.125, rely=0.125)

    start_date = Calendar(late_window, selectmode = 'day')
    start_date.place(relx=0.15, rely=0.3, anchor=CENTER)



    end_date_label = Label(late_window, text = 'End Date', font=("Arial", 13))
    end_date_label.place(relx=0.125, rely=0.48)

    end_date = Calendar(late_window, selectmode = 'day')
    end_date.place(relx=0.15, rely=0.69, anchor=CENTER)

    results_label = Label(late_window, text = 'Results', font=("Arial", 13))
    results_label.place(relx=0.4, rely=0.14)

    book_loan_info_list = []
    book_loan_info_list_tb = tksheet.Sheet(late_window, header=["Card Number", "Book Title", "Branch Name", "Days Late"], width=700, height = 500)
    book_loan_info_list_tb.grid()
    book_loan_info_list_tb.place(relx=0.4, rely=0.19)
    book_loan_info_list_tb.set_sheet_data(book_loan_info_list)

    search_button = Button(late_window, text = 'Search', width=20, height = 2, font=("Arial", 15), command=(lambda : update_book_loan_info_list(book_loan_info_list_tb, start_date.get_date(), end_date.get_date(), book_loan_info_list)))
    search_button.place(relx=0.15, rely=0.9, anchor=CENTER)

def update_borrower_info_list(list_tb, filter, input, borrower_list):
    list = sqlite3.connect('LMS.db')
    list_cur = list.cursor()
    if filter == 'None':
        list_cur.execute('''SELECT Card_No, "Borrower Name",SUM("LateFeeBalance") FROM vBookLoanInfo GROUP BY "Borrower Name" ORDER BY "LateFeeBalance" DESC''')
        borrower_list = list_cur.fetchall()
        for x in range(len(borrower_list)):
            borrower_list[x] = (borrower_list[x][0], borrower_list[x][1], '${:,.2f}'.format(borrower_list[x][2]))
        list_tb.set_sheet_data(borrower_list)
        return
    elif filter == 'Borrower ID':
        list_cur.execute('''SELECT Card_No, "Borrower Name",SUM("LateFeeBalance") FROM vBookLoanInfo WHERE Card_No = :id GROUP BY "Borrower Name"''', {'id' : input})
        borrower_list = list_cur.fetchall()
        for x in range(len(borrower_list)):
            borrower_list[x] = (borrower_list[x][0], borrower_list[x][1], '${:,.2f}'.format(borrower_list[x][2]))
        list_tb.set_sheet_data(borrower_list)
        return
    elif filter == 'Borrower Name':
        list_cur.execute('''SELECT Card_No, "Borrower Name", SUM("LateFeeBalance") FROM vBookLoanInfo WHERE "Borrower Name" = :id GROUP BY "Borrower Name"''', {'id' : input})
        borrower_list = list_cur.fetchall()
        for x in range(len(borrower_list)):
            borrower_list[x] = (borrower_list[x][0], borrower_list[x][1], '${:,.2f}'.format(borrower_list[x][2]))
        list_tb.set_sheet_data(borrower_list)
        return
    elif filter == 'Part of Borrower Name':
        list_cur.execute('''SELECT Card_No, "Borrower Name", SUM("LateFeeBalance") FROM vBookLoanInfo WHERE "Borrower Name" LIKE ? GROUP BY "Borrower Name" ORDER BY "LateFeeBalance" DESC''', ('%'+input+'%',))
        borrower_list = list_cur.fetchall()
        for x in range(len(borrower_list)):
            borrower_list[x] = (borrower_list[x][0], borrower_list[x][1], '${:,.2f}'.format(borrower_list[x][2]))
        list_tb.set_sheet_data(borrower_list)
        return

    list.commit()
    list.close()

def isFloat(num):
    try:
        float(num)
        return True
    except:
        return False

def update_book_info_list(list_tb, filter, book_list, input):
    list = sqlite3.connect('LMS.db')
    list_cur = list.cursor()
    if filter == 'None':
        list_cur.execute('''SELECT Book_Id, "Book Title", CASE WHEN "LateFeeBalance" = 0 OR "LateFeeBalance" IS NULL THEN 'Not-Applicable' ELSE "LateFeeBalance" END FROM vBookLoanInfo JOIN BOOK ON "Book Title"=Title ORDER BY "LateFeeBalance" DESC''')
        book_list = list_cur.fetchall()
        for x in range(len(book_list)):
            book_list[x] = (book_list[x][0], book_list[x][1], '${:,.2f}'.format(book_list[x][2]) if isFloat(book_list[x][2]) else book_list[x][2])
        list_tb.set_sheet_data(book_list)
        return
    elif filter == 'Book ID':
        list_cur.execute('''SELECT Book_Id, "Book Title",CASE WHEN "LateFeeBalance" = 0 OR "LateFeeBalance" IS NULL THEN 'Not-Applicable' ELSE "LateFeeBalance" END FROM vBookLoanInfo JOIN BOOK ON "Book Title"=Title WHERE Book_Id = :id''', {'id' : input})
        book_list = list_cur.fetchall()
        for x in range(len(book_list)):
            book_list[x] = (book_list[x][0], book_list[x][1], '${:,.2f}'.format(book_list[x][2]) if isFloat(book_list[x][2]) else book_list[x][2])
        list_tb.set_sheet_data(book_list)
        return
    elif filter == 'Book Title':
        list_cur.execute('''SELECT Book_Id, "Book Title",CASE WHEN "LateFeeBalance" = 0 OR "LateFeeBalance" IS NULL THEN 'Not-Applicable' ELSE "LateFeeBalance" END FROM vBookLoanInfo JOIN BOOK ON "Book Title"=Title WHERE "Book Title" = :id''', {'id' : input})
        book_list = list_cur.fetchall()
        for x in range(len(book_list)):
            book_list[x] = (book_list[x][0], book_list[x][1], '${:,.2f}'.format(book_list[x][2]) if isFloat(book_list[x][2]) else book_list[x][2])
        list_tb.set_sheet_data(book_list)
        return
    elif filter == 'Part of Book Title':
        list_cur.execute('''SELECT Book_Id, "Book Title",CASE WHEN "LateFeeBalance" = 0 OR "LateFeeBalance" IS NULL THEN 'Not-Applicable' ELSE "LateFeeBalance" END FROM vBookLoanInfo JOIN BOOK ON "Book Title"=Title WHERE "Book Title" LIKE ? ORDER BY "LateFeeBalance" DESC''',('%'+input+'%',))
        book_list = list_cur.fetchall()
        for x in range(len(book_list)):
            book_list[x] = (book_list[x][0], book_list[x][1], '${:,.2f}'.format(book_list[x][2]) if isFloat(book_list[x][2]) else book_list[x][2])
        list_tb.set_sheet_data(book_list)
        return

    list.commit()
    list.close()

# Book Loan Information Window
def open_bli_window():
    bli_window = Toplevel(root)
    bli_window.title("Book Loan Information Window")
    bli_window.geometry("1200x650")
 
    title_label = Label(bli_window, text = 'Book Loan Information', justify='center', font=("Arial", 20))
    title_label.place(relx=0.5, rely=0.05, anchor=CENTER)

    tabControl = ttk.Notebook(bli_window)
    borrower_info_tab = ttk.Frame(tabControl)
    book_info_tab = ttk.Frame(tabControl)
    tabControl.add(borrower_info_tab, text='Borrower Information')
    tabControl.add(book_info_tab, text='Book Information')
    tabControl.pack(expand=1, fill="both")

    ttk.Label(borrower_info_tab, text = "Filter", font=("Arial", 13)). place(relx=0.05, rely=0.145)
    ttk.Label(book_info_tab, text = "Filter", font=("Arial", 13)). place(relx=0.05, rely=0.145)

    clicked1 = StringVar()
    clicked1.set( "Select" )
    borrower_info = OptionMenu(borrower_info_tab, clicked1 , *["None", "Borrower ID", "Borrower Name", "Part of Borrower Name"])
    borrower_info.place(relx=0.12, rely=0.145)

    clicked2 = StringVar()
    clicked2.set( "Select" )
    book_info = OptionMenu(book_info_tab, clicked2 , *["None", "Book ID", "Book Title", "Part of Book Title"])
    book_info.place(relx=0.12, rely=0.145)

    borrower_filter = Entry(borrower_info_tab, width = 30, font=("Arial", 13))
    borrower_filter.place(relx=0.05, rely=0.195)
    book_filter = Entry(book_info_tab, width = 30, font=("Arial", 13))
    book_filter.place(relx=0.05, rely=0.195)

    ttk.Label(borrower_info_tab, text = 'Results', font=("Arial", 13)).place(relx=0.4, rely=0.145)
    ttk.Label(book_info_tab, text = 'Results', font=("Arial", 13)).place(relx=0.4, rely=0.145)

    borrower_info_list = []
    borrower_info_list_tb = tksheet.Sheet(borrower_info_tab, header=["Card Number", "Borrower Name", "Balance"], width=600, height = 500)
    borrower_info_list_tb.grid()
    borrower_info_list_tb.place(relx=0.4, rely=0.19)
    borrower_info_list_tb.set_sheet_data(borrower_info_list)

    book_info_list = []
    book_info_list_tb = tksheet.Sheet(book_info_tab, header=["Book ID", "Book Title", "Late Fee"], width=600, height = 500)
    book_info_list_tb.grid()
    book_info_list_tb.place(relx=0.4, rely=0.19)
    book_info_list_tb.set_sheet_data(book_info_list)

    search_button = Button(borrower_info_tab, text = 'Search', width=20, height = 2, font=("Arial", 15), command=(lambda : update_borrower_info_list(borrower_info_list_tb, clicked1.get(), borrower_filter.get(), borrower_info_list)))
    search_button.place(relx=0.15, rely=0.9, anchor=CENTER)

    search_button = Button(book_info_tab, text = 'Search', width=20, height = 2, font=("Arial", 15), command=(lambda : update_book_info_list(book_info_list_tb, clicked2.get(), book_info_list, book_filter.get())))
    search_button.place(relx=0.15, rely=0.9, anchor=CENTER)

title_label = Label(root, text = '  Library Database \nManagement System', justify='center', font=("Arial", 35))
title_label.place(relx=0.5, rely=0.09, anchor=CENTER)

# Check Out Book Button
cob_button = Button(root, text = 'Check Out Book', width=25, height = 1, font=("Arial", 15), command=open_cob_window)
cob_button.place(relx=0.5, rely=0.2, anchor=CENTER)

# Add Borrower Button
add_borrower_button = Button(root, text = 'Add New Borrower', width=25, height = 1, font=("Arial", 15), command=open_borrower_window)
add_borrower_button.place(relx=0.5, rely=0.27, anchor=CENTER)

# Add Book Button
add_book_button = Button(root, text = 'Add New Book', width=25, height = 1, font=("Arial", 15), command=open_add_book_window)
add_book_button.place(relx=0.5, rely=0.34, anchor=CENTER)

# List Copies Loaned Button
copies_loaned_button = Button(root, text = 'List Copies Loaned', width=25, height = 1, font=("Arial", 15), command=open_copies_window)
copies_loaned_button.place(relx=0.5, rely=0.41, anchor=CENTER)

# Late Books Query Button
late_book_query_button = Button(root, text = 'Late Books Query', width=25, height = 1, font=("Arial", 15), command=open_late_window)
late_book_query_button.place(relx=0.5, rely=0.48, anchor=CENTER)

# Book Loan Information Button
bli_button = Button(root, text = 'Book Loan Information', width=25, height = 1, font=("Arial", 15), command=open_bli_window)
bli_button.place(relx=0.5, rely=0.55, anchor=CENTER)


root.mainloop()