import pymysql
import smtplib
from email.mime.text import MIMEText
import random

password='12345'#for changing the password easier
database = "final_schema"
def select(sql):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    # build connection to database, user, password and database might be different

    cur.execute(sql) # perform the query
    u = cur.fetchall()

    cur.close()
    conn.close()
    return u # return a list


def insert(table, dic):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    if table == 'user':
        sql = "INSERT INTO user(user_name,first_name,last_name,user_Email,user_phone,account_type,user_password,user_question,user_answer,verified,user_address) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "#check if the database column name is different
        row = cur.execute(sql,(dic["username"],dic["first_name"],dic["last_name"],dic["user_email"],dic["user_phone"],dic["account_type"],dic["user_password"],dic["user_question"],dic["user_answer"],dic["verified"],dic["user_address"]))

        conn.commit()
        cur.close()
        conn.close()

# author: Haoming Zeng Details: a function to insert row to cart
def insertCart(table, dic):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    if table == 'cartlist':
        sql = "INSERT INTO cartlist(item_id,amount,buyer_id) VALUES (%s,%s,%s)"
        rows = cur.execute(sql, (dic["item_id"], dic["amount"], dic["buyer_id"]))
        conn.commit()
        cur.close()
        conn.close()

def insertPurchase(dic):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    sql = "INSERT INTO purchase(item_id, farmer_id, buyer_id, money_paid, paid_time) VALUES (%s,%s,%s,%s,%s)"
    rows = cur.execute(sql,(dic["item_id"],dic["farmer_id"],dic["buyer_id"],dic["money_paid"],dic["paytime"]))
    conn.commit()
    cur.close()
    conn.close()

def insertWishList(dic):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    sql = "INSERT INTO wishlist(item_id,amount,buyer_id) VALUES (%s,%s,%s)"
    rows = cur.execute(sql,(dic["item_id"],dic["amount"],dic["user_id"]))
    conn.commit()
    cur.close()
    conn.close()

def insertitems (table,dic,userid):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    if table == "item":
        sql = "INSERT INTO item(farmer_id,item_name,item_price,item_stock,item_details,item_categories, item_deleted) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        rows = cur.execute(sql,(userid, dic["item_name"], dic["item_price"], dic["item_stock"],dic["item_details"],dic["item_categories"],0))

        conn.commit()
        cur.close()
        conn.close()

        # rows = cur.executemany(sql, values) # if more than one row


# Vinit: This will upatate the item from file
def updateitemsfromfile(dic, itemid, farmerid):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    itemid = int(itemid[0][0])
    sql = "UPDATE item SET farmer_id = %s,item_name= %s,item_price= %s,item_stock= %s, item_details= %s, item_categories= %s WHERE item_id= %s"

    rows = cur.execute(sql, (int(farmerid), str(dic["item_name"]),int(dic["item_price"]), int(dic["item_stock"]), dic["item_details"], dic["item_categories"],itemid))
    conn.commit()
    cur.close()
    conn.close()


def update(table,query,limit,col,new_value):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    sql = "update "+table+" set "+col+"= %s"+" where "+query+"= %s"
    rows = cur.execute(sql,(new_value,limit))
    conn.commit()
    cur.close()
    conn.close()

#Mingzi Cao: ONLY used to deal with email verification
def deleteuser():
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    sql="DELETE FROM user ORDER BY user_id DESC LIMIT 1"
    rows = cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

# author: Haoming Zeng Details: remove row in cartList
def deleteCart(list_id,user_id):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    sql="DELETE FROM cartlist where item_id ="+str(list_id)+" and buyer_id ="+user_id
    rows = cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

def deleteWishList(list_id,user_id):
    conn = pymysql.connect(host='localhost', user='root', password=password, port=3306, db=database)
    cur = conn.cursor()
    sql="DELETE FROM wishlist where item_id ="+str(list_id)+" and buyer_id ="+user_id
    rows = cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

#MingziCao:randomly generate verification code
def create_verification_code():
    list_res=[]
    for i in range(0, 6):
        n = random.randint(0, 2)#choose 0-9 a-z A-Z
        if (n == 0):
            list_res.append(str(random.randint(0, 9)))
        elif (n == 1):
            list_res.append(chr(random.randrange(65, 90)))
        elif (n == 2):
            list_res.append(chr(random.randrange(97, 122)))
    return ''.join(list_res)

#MingziCao:send e-mail
def send_email_get_code(recipients):
    subject = "FarmersMarket Email Authentication"
    ver_code = create_verification_code()
    body = "This is your verification code:" + ver_code
    sender = "mciaftest@gmail.com"
    password = "ucadviqhkrqrxqcv"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()
    return ver_code

#MingziCao:send e-mail to farmer
def send_purchase_email(message,email):
    subject = "Purchase Information"
    body = message
    sender = "mciaftest@gmail.com"
    recipients = email
    password = "ucadviqhkrqrxqcv"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()
