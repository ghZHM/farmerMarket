from flask import Blueprint, request, render_template, session, redirect
import os
import models
from models import *

# database needs to be uniform and the farmer should be pass

farmersPage_bp = Blueprint('farmersPage_bp', __name__, template_folder='templates', static_folder='static',
                           static_url_path='assets')


# author: Haoming Zeng Detail: render the item and order list
@farmersPage_bp.route('/list')
def list():
    user_info = session.get('user_info')  # get username to display in the page
    userid = session.get('user_id')
    # get user_id via username and transfer it to string to complete search
    u = select("select item_name, item_price, item_stock, item_details from item where farmer_id = '" + userid + "'")
    purchase_record = select("select user_name, item_name, paid_time from purchase INNER JOIN `user` ON "
                             "`user`.user_id = purchase.farmer_id INNER JOIN item ON "
                             "item.item_id=purchase.item_id WHERE purchase.farmer_id='" + userid + "'")

    imgPath = []
    for temp in u:
        if str(temp[0]).lower() == "apple" or str(temp[0]).lower() == "grape":
            imgPath.append("/static/" + str(temp[0]).lower() + ".jpg")
        else:
            imgPath.append("/static/default.jpg")
    # generate img path via item name

    return render_template("list.html", content=u, size=len(u), user=user_info, img=imgPath)


# author: Haoming Zeng Detail: Upload item into database
@farmersPage_bp.route('/upload', methods=['POST', 'GET'])
def upload():
    error = None
    user_info = session.get('user_info')  # get username to display in the page
    userid = session.get('user_id')
    # get user_id via username and transfer it to string to complete search
    if request.method == 'POST':
        dic = {}
        dic["name"] = request.form['item-name']
        dic["price"] = request.form['item-price']
        dic["stock"] = request.form['item-stock']
        dic["details"] = request.form['item-detail']
        dic["category"] = request.form.get('category')
        # get input data from form

        temp = select("select * from item where item_name ='" + dic["name"] + "' and farmer_id = '" + userid + "'")
        # deal with duplicate data

        retMsg = ""
        if len(dic["name"]) <= 0 or len(dic["price"]) <= 0 or len(dic["stock"]) <= 0 or len(dic["details"]) <= 0:
            retMsg = "please fill all the blanks"
        elif dic["name"].isalpha() is not True or dic["details"].replace(" ", "").isalpha() is not True or dic[
            "price"].isdigit() is not True or dic["stock"].isdigit() is not True:
            retMsg = "illegal input"
        elif (float)(dic["price"]) <= 0 or (float)(dic["stock"]) < 0:
            retMsg = "number input not correct"
        elif len(temp) > 0:
            retMsg = "this good already exist"
        else:
            models.insertitems("item", dic, userid)
            retMsg = "update succeed!"
        # deal with input and rewrite database

        return redirect('/farmer/list')


# author: Haoming Zeng Detail: delete the selected item, since it might affect other row, just set it's stock to zero
@farmersPage_bp.route('/delete', methods=['POST', 'GET'])
def delete():
    user_info = session.get('user_info')  # get username to display in the page
    userid = session.get('user_id')
    # get user_id via username and transfer it to string to complete search

    if request.method == 'POST':
        u = select(
            "select item_name, item_price, item_stock, item_details from item where farmer_id = '" + userid + "'")

        json_value = request.get_json()
        index = json_value['id']
        # get front-end input via json

        selected_item = u[index][0]
        models.update("item", "item_name", selected_item, "item_stock", 0)
        # get selected item and perform fake delete

    return redirect('/farmer/list')


# author: Haoming Zeng Detail: modify item's property
@farmersPage_bp.route('/update', methods=['POST', 'GET'])
def update():
    user_info = session.get('user_info')  # get username to display in the page
    userid = session.get('user_id')
    # get user_id via username and transfer it to string to complete search
    u = select("select item_name, item_price, item_stock, item_details from item where farmer_id = '" + userid + "'")

    if request.method == 'POST':
        json_value = request.get_json()
        price = json_value['price']
        stock = json_value['stock']
        details = json_value['detail']
        index = json_value['id']
        # get front end json input
        item = u[index][0]
        # get the item name

        if len(price.strip()) > 0:
            if price.strip().isdigit() and float(price.strip()) > 0:
                models.update("item", "item_name", item, "item_price", price)

        if len(stock.strip()) > 0:
            if stock.strip().isdigit() and float(stock.strip()) > 0:
                models.update("item", "item_name", item, "item_stock", stock)

        if len(details.strip()) > 0:
            models.update("item", "item_name", item, "item_details", details)
        # perform query in update

    return redirect('/farmer/list')


@farmersPage_bp.route('/order', methods=['POST', 'GET'])
def order():
    user_info = session.get('user_info')  # get username to display in the page
    userid = session.get('user_id')
    purchase_record = select("select user_name, item_name, paid_time from purchase INNER JOIN `user` ON "
                             "`user`.user_id = purchase.farmer_id INNER JOIN item ON "
                             "item.item_id=purchase.item_id WHERE purchase.farmer_id='" + userid + "'")
    return render_template('orders.html', size=len(purchase_record), user=user_info, purchase=purchase_record)


#Auther Vinit : This methods deals with uploading the items with file
@farmersPage_bp.route('/fileupload', methods=['POST', 'GET'])
def file_upload():
    if request.method == 'GET':
        return render_template('file_upload.html', user=session.get('user_info'))
    if request.method == 'POST':
        userid = session.get('user_id')  # get userid by Haoming Zeng
        # print("UserId : " + userid)
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
                print(str(len(list)))
                count = 0
                for i in list:
                    print("here1")
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
                                item_dic["name"] = row[0].strip()
                                item_dic["price"] = row[1].strip()
                                item_dic["stock"] = row[2]
                                item_dic["details"] = row[3]
                                item_dic["category"] = row[4].strip()

                                temp = select("select * from item where item_name ='" + item_dic[
                                    "name"] + "' and farmer_id = '" + userid + "'")
                                print("temp Len " + str(len(temp)))
                                if item_dic["name"].replace(" ", "").isalpha() is not True:
                                    msg = "Please provide valid item name line:" + str(count)
                                    break
                                elif item_dic["price"].isdigit() is not True:
                                    msg = "Please provide valid item price line:" + str(count)
                                    break
                                elif item_dic["stock"].isdigit() is not True:
                                    msg = "Please provide valid item stock line:" + str(count)
                                    break
                                elif float(item_dic["price"]) <= 0:
                                    msg = "Please provide valid item price line:" + str(count)
                                    break
                                elif float(item_dic["stock"]) < 0:
                                    msg = "Please provide valid stock line:" + count
                                    break
                                elif len(temp) > 0:
                                    print("inserted count:" + str(count) + " " + item_dic["name"])
                                    exists_items[count] = item_dic["name"]
                                    itemid = select("select item_id from item where item_name ='" + item_dic["name"] +
                                                    "' and farmer_id = '" + userid + "'")
                                    models.updateitemsfromfile(item_dic, itemid, userid)
                                    count += 1
                                else:
                                    models.insertitems("item", item_dic, userid)
                                    item_inserted[count] = item_dic["name"]
                                    count += 1
        f.close()
        if os.path.exists(f.filename):
            os.remove(f.filename)
        else:
            print("The file does not exist")
        # list = "Items already exist - items: " + str(exists_items) + "\n"
        # list1 = "Items inserted - items: " + str(item_inserted) + "\n"
        # print(msg + "\n" + str(list) + "\n"+ str(list1))
        """if (len(item_inserted) !=0) and (len(exists_items) !=0):
            list1 = "Items inserted - items: " + str(item_inserted) + "\n"
            return render_template("file_upload.html", msg=msg, list=list, list1=list1, total=count)
        elif len(exists_items) !=0 :
            return render_template("file_upload.html", msg=msg, list=list, list1="", total=count)
        elif len(item_inserted) !=0 :
            return render_template("file_upload.html", msg=msg, list="", list1=list1, total=count)
        else:"""
        if msg =="":
            msg= "Successfully Uploaded."
        return render_template("file_upload.html", msg=msg)
