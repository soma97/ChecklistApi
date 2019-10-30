import pyodbc
from contextlib import contextmanager
import re
import datetime
from Item import Item

@contextmanager
def executeTransaction(conn):
    print('Starting query')
    try:
        yield
    finally:
        conn.commit()
        print('Ending query')
    return conn.cursor()

class DB_access:

    def connect(self):
        self.conn = pyodbc.connect("Driver={SQL Server};Server=CTBLHP4\\SQLEXPRESS;Database=checklistDB;Trusted_Connection=True;")
        self.cursor=self.conn.cursor()

    def __init__(self):
        self.connect()

    def check_conn(self):
        try:
            self.conn.cursor().execute("SELECT @@version")
            print('OK')
        except Exception as e:
            print(e)
            return self.connect()

    def check_arg(self,arg): #check for legal argument
        match = re.findall("[A-Za-z]+[0-9_]*",str(arg))
        print(arg+ str(len(match)))
        if len(match) != 1:
            raise Exception

    def insert_user(self,user):
        self.check_arg(user)
        with executeTransaction(self.conn):
            self.cursor.execute("INSERT INTO [checklist].[user] VALUES(?)",(user))


    def insert_checklist(self,checklist):
        with executeTransaction(self.conn):
            self.cursor.execute("SELECT COUNT(*) FROM [checklist].[checklist]")
            checklist_id= int(self.cursor.fetchall()[0][0])*1000
            self.cursor.execute("SELECT COUNT(*) FROM [checklist].[checklist] WHERE id=?",(checklist_id))
            while(int(self.cursor.fetchall()[0][0])!=0):
                checklist_id+=1000
                self.cursor.execute("SELECT COUNT(*) FROM [checklist].[checklist] WHERE id=?",(checklist_id))

            self.cursor.execute("INSERT INTO [checklist].[checklist](id,name,username) VALUES(?,?,?)", (checklist_id,checklist.name,checklist.username))


    def insert_item(self,checklist_id,item):
        with executeTransaction(self.conn):
            self.cursor.execute("SELECT COUNT(*) FROM [checklist].[item] WHERE chk_id=?",(checklist_id))
            item_id=checklist_id+int(self.cursor.fetchall()[0][0])+1
            print(item_id)
            self.cursor.execute("INSERT INTO [checklist].[item](id,name,date_time,item_freq,done,chk_id) VALUES(?,?,?,?,?,?)", (item_id,item.name,item.date_time,item.item_freq,item.done,checklist_id))
            return item_id

    def set_done(self,item_id,is_done):
        with executeTransaction(self.conn):
            self.cursor.execute("UPDATE [checklist].[item] set done=? WHERE id=?",(is_done,item_id))

    def get_checklist_for_name(self,username):
        with executeTransaction(self.conn):
            self.cursor.execute("SELECT * FROM [checklist].[checklist] WHERE username=?",(username))
            chklist=self.cursor.fetchall()
            if len(chklist)==0:
                raise Exception
            return chklist

    def get_items_for_checklist(self,chk_id):
        with executeTransaction(self.conn):
            self.cursor.execute("SELECT * FROM [checklist].[item] WHERE chk_id=?", (chk_id))
            res=self.cursor.fetchall()
            if len(res)==0:
               raise Exception
            return res

    def delete_checklist(self,chk_id,username):
        with executeTransaction(self.conn):
            self.cursor.execute("DELETE FROM [checklist].[checklist] WHERE id=? and username=?", (chk_id,username))
    
    def delete_item(self,item_id):
        with executeTransaction(self.conn) as exT:
            print(exT)
            self.cursor.execute("DELETE FROM [checklist].[item] WHERE id=?", (item_id))