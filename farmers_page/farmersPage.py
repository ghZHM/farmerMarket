
from flask import Blueprint, request, render_template, session, redirect, flash
import os
import models
from models import *


farmersPage_bp = Blueprint('farmersPage_bp', __name__, template_folder='templates', static_folder='static',
                           static_url_path='assets')


# author: Haoming Zeng Detail: render the item and order list
@farmersPage_bp.route('/list')
def list():
    user_info = str(session.get('user_info'))  # get username to display in the page
    userid = str(session.get('user_id'))
    # get user_id via username and transfer it to string to complete search
    u = select("select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_deleted = 0 and farmer_id = '" + userid + "'")

    imgPath = []
    prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
    for temp in u:
        if str(temp[5]).lower() in prefixCategory:
            imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
        else:
            imgPath.append("/static/default.jpg")
    # generate img path via item category

    return render_template("list.html", content=u, size=len(u), user=user_info, img=imgPath)


# author: Haoming Zeng Detail: Upload item into database
@farmersPage_bp.route('/upload', methods=['POST', 'GET'])
def upload():
    error = None
    userid = str(session.get('user_id'))
    # get user_id via username and transfer it to string to complete search
    if request.method == 'POST':
        json_value = request.get_json()
        name = json_value['item_name'].strip()
        price = json_value['item_price']
        stock = json_value['item_stock']
        detail = json_value['item_details']
        category = json_value['item_category']
        # get input data from form

        temp = select("select * from item where item_deleted = 0 and item_name ='" + name + "' and farmer_id = '" + userid + "'")
        # deal with duplicate data

        retMsg = ""
        if len(name) <= 0 or len(price) <= 0 or len(stock) <= 0 or len(detail) <= 0:
            retMsg = "please fill all the blanks"
        elif name.replace(" ", "").isalpha() is not True or detail.replace(" ","").isalpha() is not True or price.replace(
            ".", "", 1).isdigit() is not True or stock.isdigit() is not True:
            retMsg = "illegal input"
        elif (float)(price) <= 0 or (float)(stock) < 0:
            retMsg = "number input not correct"
        elif len(temp) > 0:
            retMsg = "this good already exist"
        else:
            dic = {}
            dic["item_name"] = name
            dic["item_price"] = price
            dic["item_stock"] = stock
            dic["item_details"] = detail
            dic["item_categories"] = category
            models.insertitems("item", dic, userid)

        print(retMsg)
        # deal with input and rewrite database
        return redirect('/farmer/list')


# author: Haoming Zeng Detail: delete the selected item, since it might affect other row, just set it's stock to zero
@farmersPage_bp.route('/delete', methods=['POST', 'GET'])
def delete():
    userid = str(session.get('user_id'))
    # get user_id via username and transfer it to string to complete search

    if request.method == 'POST':
        u = select(
            "select item_id from item where item_deleted = 0 and farmer_id = '" + userid + "'")

        json_value = request.get_json()
        index = json_value['id']
        # get front-end input via json

        selected_item = u[index][0]
        models.update("item", "item_id", selected_item, "item_deleted", 1)


    return redirect('/farmer/list')


# author: Haoming Zeng Detail: modify item's property
@farmersPage_bp.route('/update', methods=['POST', 'GET'])
def update():
    userid = str(session.get('user_id'))
    # get user_id via username and transfer it to string to complete search
    u = select("select item_id, item_price, item_stock, item_details from item where item_deleted = 0 and farmer_id = '" + userid + "'")

    if request.method == 'POST':
        json_value = request.get_json()
        price = json_value['price']
        stock = json_value['stock']
        details = json_value['detail']
        index = json_value['id']
        # get front end json input
        item = u[index][0]
        # get the item name

        if len(price) > 0:
            if price.replace(".", "", 1).isdigit() and float(price) > 0:
                models.update("item", "item_id", item, "item_price", price)

        if len(stock) > 0:
            if stock.strip().isdigit() and float(stock.strip()) > 0:
                models.update("item", "item_id", item, "item_stock", stock)

        if len(details) > 0:
            models.update("item", "item_id", item, "item_details", details)
        # perform query in update

    return redirect('/farmer/list')

# Author Jialin Yang Details: perform search based on category on farmers page
@farmersPage_bp.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        user_info = session.get('user_info')
        category = str(request.form.get('category'))
        userid = str(session.get('user_id'))

        # perform query based on conditions
        if category == "all":
            goods = select(
                "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_stock > 0 and item_deleted = 0 and farmer_id = '"+userid+"'")
        else:
            goods = select(
                "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_stock > 0 and item_deleted = 0 and item_categories ='" + category + "'" +" and farmer_id = '"+userid+"'")

        # generate image path based on category
        imgPath = []
        prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
        for temp in goods:
            if str(temp[5]).lower() in prefixCategory:
                imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
            else:
                imgPath.append("/static/default.jpg")

        return render_template("list.html", content=goods, size=len(goods), user=user_info, img=imgPath)


# Author Haoming Zeng Detail: display order query by farmer_id
@farmersPage_bp.route('/order', methods=['POST', 'GET'])
def order():
    user_info = session.get('user_info')  # get username to display in the page
    userid = str(session.get('user_id'))

    purchase_record = select(
        "select user.user_name, money_paid, paid_time, item.item_name from purchase INNER JOIN `user` ON "
        "`user`.user_id = purchase.buyer_id INNER JOIN item ON "
        "item.item_id=purchase.item_id WHERE purchase.farmer_id='" + userid + "'")
    return render_template('orders.html', size=len(purchase_record), user=user_info, purchase=purchase_record)


# Auther Vinit : This methods deals with uploading the items with file
@farmersPage_bp.route('/fileupload', methods=['POST', 'GET'])
def file_upload():
    if request.method == 'POST':
        userid = str(session.get('user_id'))  # get userid by Haoming Zeng
        userid = str(userid)  # casting the userid in string
        f = request.files['file']
        f.save(f.filename)

        list = {}
        list1 = {}
        msg = ""
        item_dic = {}  # dictionary for storing items
        exists_items = {}  # dictionary for storing list of already
        item_inserted = {}
        count = 0
        print(f.filename.endswith(".csv"))
        if not f.filename.endswith(".csv"):  # checking for file type
            msg = "Only CSV files are allowed"
        else:
            print("here")
            # saving file inorder to read
            with open(f.filename, 'r') as data:
                list = data.readlines()  # storing all the lines in the list
                count = 0
                for i in list:
                    if count == 0:
                        count += 1  # igoring the first line
                    else:
                        row = i.split(',')
                        if len(row) > 5 or len(row) < 5:
                            msg = " Please check blank values line:" + str(count)
                        else:
                            if (len(row[0]) == 0 or len(row[1]) == 0 or len(row[2]) == 0 or len(row[3]) == 0 or len(
                                    row[4]) == 0):
                                msg = "Please check the blank values at line: " + str(count)
                                break
                            else:
                                item_dic["item_name"] = row[0].strip()
                                item_dic["item_price"] = row[1].strip()
                                item_dic["item_stock"] = row[2]
                                item_dic["item_details"] = row[3]
                                item_dic["item_categories"] = row[4].strip()

                                temp = select("select * from item where item_name ='" + item_dic[
                                    "item_name"] + "' and farmer_id = '" + userid + "'")
                                if item_dic["item_name"].replace(" ", "").isalpha() is not True:
                                    msg = "Please provide valid item name line:" + str(count)
                                    break
                                elif item_dic["item_price"].isdigit() is not True:
                                    msg = "Please provide valid item price line:" + str(count)
                                    break
                                elif item_dic["item_stock"].isdigit() is not True:
                                    msg = "Please provide valid item stock line:" + str(count)
                                    break
                                elif float(item_dic["item_price"]) <= 0:
                                    msg = "Please provide valid item price line:" + str(count)
                                    break
                                elif float(item_dic["item_stock"]) < 0:
                                    msg = "Please provide valid stock line:" + count
                                    break
                                elif len(temp) > 0:
                                    exists_items[count] = item_dic["item_name"]
                                    itemid = select("select item_id from item where item_name ='" + item_dic["item_name"] +
                                                    "' and farmer_id = '" + userid + "'")
                                    models.updateitemsfromfile(item_dic, itemid, userid)
                                    count += 1
                                    msg = "Successfully Updated"
                                else:
                                    models.insertitems("item", item_dic, userid)
                                    item_inserted[count] = item_dic["item_name"]
                                    count += 1
                                    msg = "Successfully Updated"
        f.close()
        if os.path.exists(f.filename):
            os.remove(f.filename)
        else:
            msg = "File is not exist."
        flash(msg)
        user_info = session.get('user_info')  # get username to display in the page
        userid = session.get('user_id')
        # get user_id via username and transfer it to string to complete search
        u = select(
            "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_deleted = 0 and farmer_id = '" + userid + "'")

        imgPath = []
        prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
        for temp in u:
            if str(temp[5]).lower() in prefixCategory:
                imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
            else:
                imgPath.append("/static/default.jpg")
        # generate img path via item name
        # tkinter.messagebox.showinfo("Success", "Successfully Uploaded.")
        msg = "Successfully Uploaded"
        return render_template("list.html", content=u, size=len(u), user=user_info, img=imgPath)


# Author Jialin Yang : This is a method of logout
@farmersPage_bp.route('/signout', methods=['GET', "POST"])
def signout():
    user_info = session.get('user_info')
    session.pop('user_info')
    return redirect('/home/login')

