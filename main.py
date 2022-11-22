from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
import qrcode
from PIL import ImageTk, Image
import os.path

global name_val, username_val, password_val, link_val, counter

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
)
cur = db.cursor()

cur.execute('Create database if not exists QRCodeGenerator;')
cur.execute('Use QRCodeGenerator;')

cur.execute('Create table if not exists users(username varchar(50) primary key, name varchar(100), password varchar(100));')
cur.execute('Create table if not exists links(id int auto_increment,username varchar(50), link varchar(255) not null, qrcode varchar(1000), primary key(id, username), foreign key(username) references users(username));')
cur.execute('Select * from users where username="Guest";')
data= cur.fetchall()
if data:
    pass
else:
    cur.execute('Insert into users(username, name, password) values("Guest","Guest","Guest");')

db.commit()

root = Tk()
root.title('QR Code Generator')
root.geometry('500x500')

def homePage():

    def show_image(addr):
        image1 = Image.open(addr)
        img1 = image1.resize((130,130), Image.ANTIALIAS)
        test = ImageTk.PhotoImage(img1)

        label1 = Label(root,image=test)
        label1.image = test
        label1.place(x=320, y=100)

#############################################################################################################

# Main

    def main(username='Guest',name="Guest"):

        def GetValue(event):
            link_inp.delete(0, END)
            row_id = tree.selection()[0]
            select = tree.set(row_id)
            link_inp.insert(0,select['Links'])
        
        def View():
            global counter 
            counter = 1
            cur.execute(f'select id, link from links where username = "{username}"')
            tableData = cur.fetchall()
            for data in tableData:
                tree.insert(parent='', index='end', text='', values=(counter,data[1]))
                counter += 1

        def last_row():
            global counter
            cur.execute(f'select id, link from links where username = "{username}"')
            tableData = cur.fetchall()
            tree.insert(parent='', index='end', text='', values=(counter,tableData[-1][1]))
            counter += 1

        def qrcodeGen():
            file_exists = True
            checker = 0
            link = link_val.get()
            img = qrcode.make(link)
            while(file_exists):
                checker += 1
                file_exists = os.path.exists(f'images\{username+"_"+str(checker)}.jpg')
            addr = f'images\{username+"_"+str(checker)}.jpg'
            img.save(addr)
            cur.execute(f'Insert into links(username, link, qrcode) values("{username}","{link}","{addr}");')
            show_image(addr)
            last_row()

        for item in Frame.winfo_children(root):
            item.destroy()
            
        mainFrame = Frame(root, width=500, height=500)
        mainFrame.pack()

        mainPage = Label(mainFrame, text = 'QR Code Generator', font=('Yu Gothic UI Semibold',15))
        mainPage.place(x=170, y = 30)

        welcomeMessage = Label(mainFrame, text = f'Welcome {name}', font=('Yu Gothic UI',9))
        welcomeMessage.place(x=380, y = 15)

        link = Label(mainFrame, text = 'Link :', font =('Yu Gothic UI',10))
        link.place(x=40, y = 100)

        link_val = StringVar()

        link_inp = Entry(mainFrame, textvariable=link_val,width=35)
        link_inp.place(x=80, y = 105)

        createButton = Button(mainFrame, text='Create', font=(0,10), width=7, command=qrcodeGen)
        createButton.place(x = 80, y = 140)

        backButton = Button(mainFrame, text='Back', font=(0,10), width=7, command=home)
        backButton.place(x = 50, y = 20)

        tree = ttk.Treeview(mainFrame)
        tree['columns'] = ('ID', 'Links')

        tree.column("#0", width = 0, stretch=NO)
        tree.column('ID',anchor=CENTER,width=30)
        tree.column('Links',anchor=CENTER,width=300)

        tree.heading('ID',text='Id', anchor=CENTER)
        tree.heading('Links',text='Links',anchor=CENTER)

        View()
        tree.place(x=60,y=250)
        tree.bind('<Double-Button-1>',GetValue)

        root.bind('<Return>',lambda event:qrcodeGen())  

#############################################################################################################

# Login

    def loginPage():
        def submit():
            username = username_val.get()
            password = password_val.get()
            cur.execute(f'select * from users where username = \'{username}\' and password = \'{password}\';')
            data = cur.fetchall()
            if data:
                main(username,data[0][1])  
            else:
                error1 = Label(loginFrame, text = 'ERROR! Wrong username or password! \n\n Please SignUp to Create new account!', font=('Yu Gothic UI Semibold',12), fg='dark red')
                error1.place(x=100, y = 320)  
                tempButton = Button(loginFrame, text='SignUp', font=(0,10), width=7, command=signUpPage)
                tempButton.place(x = 200, y = 400)
        for item in Frame.winfo_children(root):
            item.destroy()
            
        loginFrame = Frame(root, width=500, height=500)
        loginFrame.pack()

        loginPage = Label(loginFrame, text = 'Login Page', font=('Yu Gothic UI Semibold',20))
        loginPage.place(x=180, y = 70)

        username = Label(loginFrame, text = 'Username :', font =('Yu Gothic UI Semibold',12))
        username.place(x=50, y = 190)
        password = Label(loginFrame, text = 'Password :', font =('Yu Gothic UI Semibold',12))
        password.place(x=50, y = 220)

        username_val = StringVar()
        password_val = StringVar()

        username_inp = Entry(loginFrame, textvariable=username_val,width=25)
        username_inp.place(x=150, y = 195)
        password_inp = Entry(loginFrame, textvariable=password_val,width=25, show='*')
        password_inp.place(x=150, y = 225)
 
        submitButton = Button(loginFrame, text='Submit', font=(0,10), width=7, command=submit)
        submitButton.place(x = 200, y = 270)

        backButton = Button(loginFrame, text='Back', font=(0,10), width=7, command=home)
        backButton.place(x = 50, y = 20)

        root.bind('<Return>',lambda event:submit())  

#############################################################################################################

# Sign Up

    def signUpPage():  
        def submit():
            name = name_val.get()
            username = username_val.get()
            password = password_val.get()
            cur.execute(f'select * from users where username = \'{username}\';')
            data = cur.fetchall()
            if data:
                error1 = Label(signUpFrame, text = 'Sorry, User already exists!', font=(0,12))
                error1.place(x=140, y = 320)
                error1.after(1000,error1.destroy)   
            else:
                if(name and username and password):
                    cur.execute(f'Insert into users(username, name, password) values(\'{username}\',\'{name}\',\'{password}\');')
                    db.commit()
                    messagebox.showinfo("Information", "User Added!")
                else:
                    error1 = Label(signUpFrame, text = 'ERROR: Please enter appropriate response!', font=('Yu Gothic UI Semibold',12), fg='dark red')
                    error1.place(x=100, y = 320)  
                    error1.after(1000,error1.destroy)   

        for item in Frame.winfo_children(root):
            item.destroy()
        
        signUpFrame = Frame(root, width=500, height=500)
        signUpFrame.pack()

        signPage = Label(signUpFrame, text = 'Signup Page', font=('Yu Gothic UI Semibold',20))
        signPage.place(x=180, y = 70)

        name = Label(signUpFrame, text = 'Name :', font =('Yu Gothic UI Semibold',12))
        name.place(x=50, y = 160)
        username = Label(signUpFrame, text = 'Username :', font =('Yu Gothic UI Semibold',12))
        username.place(x=50, y = 190)
        password = Label(signUpFrame, text = 'Password :', font =('Yu Gothic UI Semibold',12))
        password.place(x=50, y = 220)

        name_val = StringVar()
        username_val = StringVar()
        password_val = StringVar()

        name_inp = Entry(signUpFrame, textvariable=name_val,width=25)
        name_inp.place(x=150, y = 165)
        username_inp = Entry(signUpFrame, textvariable=username_val,width=25)
        username_inp.place(x=150, y = 195)
        password_inp = Entry(signUpFrame, textvariable=password_val,width=25, show='*')
        password_inp.place(x=150, y = 225)

        submitButton = Button(signUpFrame, text='Submit', font=(0,10), width=7, command=submit)
        submitButton.place(x = 200, y = 270)

        loginButton = Button(signUpFrame, text='Login', font=(0,10), width=7, command=loginPage)
        loginButton.place(x = 400, y = 20)

        backButton = Button(signUpFrame, text='Back', font=(0,10), width=7, command=home)
        backButton.place(x = 50, y = 20)


        root.bind('<Return>',lambda event:submit())     

#############################################################################################################

# QUIT

    def end():
        quit()

#############################################################################################################

# Homepage

    def home():
        for item in Frame.winfo_children(root):
            item.destroy()

        homeFrame = Frame(root, width=500, height=500)
        homeFrame.pack()

        homePage = Label(homeFrame, text = 'QR Code Generator', font=('Helvetica 15 bold'))
        homePage.place(x = 170, y= 100)

        signupButton = Button(homeFrame, text = 'Sign Up', font=(0,10), width=7, command=signUpPage)
        signupButton.place(x = 220, y = 200)

        loginButton = Button(homeFrame, text = 'Login', font=(0,10), width=7, command=loginPage)
        loginButton.place(x = 220, y = 250)

        guestuserButton = Button(homeFrame, text = 'Guest', font=(0,10), width=7, command=main)
        guestuserButton.place(x = 220, y= 300)

        quitButton = Button(homeFrame, text = 'Quit', font=(0,10), width=7,command= end)
        quitButton.place(x = 220, y= 350)

    home()

homePage()
root.mainloop()
cur.execute('Delete from links where username = "Guest";')
cur.execute('Delete from users where username = "Guest";')
db.commit()
cur.close()
db.close()