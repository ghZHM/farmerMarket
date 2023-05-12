from flask import Blueprint, request, render_template, session, redirect, jsonify, flash
import os
import models
from models import *
from datetime import datetime
import paypalrestsdk

purchase_bp = Blueprint('purchase_bp', __name__, template_folder='templates', static_folder='static',
                        static_url_path='assets')

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "", # removed key
    "client_secret": "" # removed key
})


# Author: Haoming Zeng Details: select all the product from database and render the page
@purchase_bp.route('/purchase')
def purchase():
    user_info = session.get('user_info')
    goods = select(
        "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_deleted = 0 and item_stock > 0 order by item_name, item_price")

    # generate picture path
    imgPath = []
    prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
    for temp in goods:
        if str(temp[5]).lower() in prefixCategory:
            imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
        else:
            imgPath.append("/static/default.jpg")

    return render_template("purchasePage.html", content=goods, size=len(goods), user=user_info, img=imgPath)


# Author: Haoming Zeng Details: select product from database based on category and render the page
@purchase_bp.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        user_info = session.get('user_info')
        category = str(request.form.get('category'))

        # perform query based on conditions
        if category == "all":
            goods = select(
                "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_deleted = 0 and item_stock > 0 order by item_name, item_price")
        else:
            goods = select(
                "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_stock > 0 and item_deleted = 0 and item_categories ='" + category + "'"+ " order by item_name, item_price")

        # generate image path based on name
        imgPath = []
        prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
        for temp in goods:
            if str(temp[5]).lower() in prefixCategory:
                imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
            else:
                imgPath.append("/static/default.jpg")

        return render_template("purchasePage.html", content=goods, size=len(goods), user=user_info, img=imgPath)


# Author: Haoming Zeng Details: select row from database via user_id and render the cart
@purchase_bp.route('/cart', methods=['POST', 'GET'])
def cart():
    if request.method == "GET":
        user_info = str(session.get('user_info'))
        user_id = str(session.get('user_id'))
        # to fix user_id
        # perform query based on user_id
        cartObjects = select(
            "select  cartlist.item_id, item.item_name, item.item_details, item.item_price, cartlist.amount, item.item_categories from cartlist INNER JOIN item ON cartlist.item_id = item.item_id where item_deleted = 0 and buyer_id ='" + user_id + "'")

        imgPath = []
        totalPrice = []
        sum = 0
        prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
        for temp in cartObjects:
            if str(temp[5]).lower() in prefixCategory:
                imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
            else:
                imgPath.append("/static/default.jpg")
            totalPrice.append(float(temp[3]) * int(temp[4]))
            sum += float(temp[3]) * int(temp[4])  # calculate the sum price of the cart

        return render_template("cart.html", img=imgPath, content=cartObjects, size=len(cartObjects), user=user_info, total=totalPrice,
                               sumPrice=sum)


# Author: Haoming Zeng Details: add or update the cart
@purchase_bp.route('/addCart', methods=['POST', 'GET'])
def addCart():
    if request.method == "POST":
        # get front-end input via ajax
        json_value = request.get_json()
        amount = json_value["amount"]
        itemid = json_value["id"]
        user_id = str(session.get('user_id'))
        stock = select("select item_stock from item where item_id =" + str(itemid))
        msg = "successful added"
        if amount.isdigit() and 0 < int(amount) <= int(stock[0][0]):
            # search if the user has added the same product to cart
            cart_itemid = select(
                "select cartlist_id from cartlist where item_id =" + str(itemid) + " and buyer_id ='" + user_id + "'")
            if len(cart_itemid) <= 0:
                # create new row in cartlist
                dic = {}
                dic["item_id"] = itemid
                dic["amount"] = amount
                dic["buyer_id"] = user_id
                insertCart("cartlist", dic)
            else:
                # update on the previous row
                cart_itemid = str(cart_itemid[0][0])
                amountInCart = select("select amount from cartlist where cartlist_id =" + cart_itemid)[0][0]
                if int(amount) + int(amountInCart) <= int(stock[0][0]):
                    update("cartlist", "cartlist_id", cart_itemid, "amount", int(amount) + int(amountInCart))
                else:
                    msg = "ran out of stock"
        else:
            msg = "input error or out of stock"
        flash(msg)
    return redirect("/purchase/cart")


# Author: Haoming Zeng Details: remove row from the cart
@purchase_bp.route('/removeCart', methods=['POST', 'GET'])
def removeCart():
    if request.method == "POST":
        json_value = request.get_json()
        itemid = json_value["id"]
        userid = str(session.get('user_id'))
        deleteCart(itemid, userid)  # perform delete
        return redirect("/purchase/cart")


# Author: Haoming Zeng Details: refresh the cart page and database after modify
@purchase_bp.route('/refreshCart', methods=['POST', 'GET'])
def refreshCart():
    if request.method == "POST":

        json_value = request.get_json()
        itemid = str(json_value["id"])
        userid = str(session.get('user_id'))
        new_amount = json_value["new_amount"]
        cartlist_id = str(
            select("select cartlist_id from cartlist where item_id = '" + itemid + "' and buyer_id = '" + userid + "'")[
                0][0])
        currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
        if new_amount.isdigit() and 0 < int(new_amount) <= currentStock:
            update("cartlist", "cartlist_id", cartlist_id, "amount", new_amount)
        return redirect("/purchase/cart")

# Author Jialin Yang, Mingzi Cao Details: perform purchase integrate with paypal
@purchase_bp.route('/payment', methods=['POST'])
def payment():
    user_info = str(session.get('user_info'))
    user_id = str(session.get('user_id'))
    List = select("select item_id, amount from cartlist where buyer_id='" + user_id + "'")
    sum = 0
    toPurchase=[]
    for temp in List:
        itemid = str(temp[0])
        amount = int(temp[1])
        currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
        if currentStock >= int(amount) > 0:
            toPurchase.append(itemid)
            itemInfo = select("select farmer_id, item_price from item where item_id =" + str(itemid))
            sum += amount * float(itemInfo[0][1])


    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/purchase/execute",
            "cancel_url": "http://localhost:3000/purchase/cart"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "price": sum,
                    "currency": "GBP",
                    "quantity": 1}
                ]},
            "amount": {
                "total": sum,
                "currency": "GBP"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        session['purchase'] = toPurchase
        print('Payment success!')

    else:
        print(payment.error)
    return jsonify({'paymentID': payment.id})


@purchase_bp.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id': request.form['payerID']}):
        user_info = str(session.get('user_info'))
        print('Execute success!')
        user_id = str(session.get('user_id'))
        List = select("select item_id, amount from cartlist where buyer_id='" + user_id + "'")
        toPurchase = session.get('purchase')
        for temp in List:
            itemid = str(temp[0])
            amount = int(temp[1])
            currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
            if itemid in toPurchase:
                paytime = str(datetime.now().strftime("%F %H:%M:%S"))
                address = str(select("select user_address from user where user_id=" + user_id)[0][0])
                itemInfo = select("select farmer_id, item_price, item_name from item where item_id =" + str(itemid))
                dic = {}
                dic["item_id"] = itemid
                dic["item_name"] = str(itemInfo[0][2])
                dic["farmer_id"] = str(itemInfo[0][0])
                farmerInfo = select("select first_name, user_Email from user where user_id ='"+str(itemInfo[0][0])+"'")
                dic["farmer_name"] =str(farmerInfo[0][0])
                dic["buyer_id"] = user_id
                dic["money_paid"] = amount * float(itemInfo[0][1])
                dic["address"] = address
                dic["paytime"] = paytime
                dic["amount"] = amount
                dic["buyer_name"] = user_info
                dic["email"]=str(farmerInfo[0][1])
                # sum += amount * float(itemInfo[0][1])
                insertPurchase(dic)
                update("item", "item_id", itemid, "item_stock", currentStock - amount)
                deleteCart(itemid, user_id)
                msg = "Hello " + dic["farmer_name"] + ",\n" + dic["buyer_name"] + " has bought " + str(
                    dic["amount"]) + " of " + dic["item_name"] + " and paid: " + str(dic["money_paid"])
                msg = msg + "\n" + "Please send the item to:" + dic["address"] + "\nPurchase made at " + dic["paytime"]
                print(msg)
                send_purchase_email(msg, dic["email"])
        success = True
    else:
        print(payment.error)

    return jsonify({'success': success})



# Author: Haoming Zeng Details: query from database and render the front end page
@purchase_bp.route('/wishlist', methods=['POST', 'GET'])
def wishList():
    user_info = str(session.get('user_info'))
    userid = str(session.get('user_id'))
    if request.method == "GET":
        wishListObjects = select(
            "select wishlist.item_id, item.item_name, item.item_details, item.item_price, wishlist.amount, item.item_categories from wishlist INNER JOIN item ON wishlist.item_id = item.item_id where buyer_id ='" + userid + "'")

        imgPath = []
        totalPrice = []
        sum = 0
        prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
        for temp in wishListObjects:
            if str(temp[5]).lower() in prefixCategory:
                imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
            else:
                imgPath.append("/static/default.jpg")
            totalPrice.append(float(temp[3]) * int(temp[4]))
            sum += float(temp[3]) * int(temp[4])

        return render_template("wishList.html", img=imgPath, content=wishListObjects, size=len(wishListObjects),
                               total=totalPrice,
                               sumPrice=sum, user=user_info)

# Author: Mingzi Cao Detail: add items in purchase page into wishlist
@purchase_bp.route('/addwishlist', methods=['POST', 'GET'])
def addWishList():
    if request.method == "POST":
        json_value = request.get_json()
        amount = json_value["amount"]
        itemid = json_value["id"]
        user_id = str(session.get('user_id'))

        if amount.isdigit() and 0 < int(amount):
            cart_itemid = select(
                "select wishlist_id from wishlist where item_id =" + str(itemid) + " and buyer_id ='" + user_id + "'")
            if len(cart_itemid) <= 0:
                dic = {}
                dic["item_id"] = itemid
                dic["amount"] = amount
                dic["user_id"] = user_id
                insertWishList(dic)
            else:
                cart_itemid = str(cart_itemid[0][0])
                amountInCart = select("select amount from wishlist where wishlist_id =" + cart_itemid)[0][0]
                update("wishlist", "wishlist_id", cart_itemid, "amount", int(amount) + int(amountInCart))

    return redirect("/purchase/purchase")


# Author: Mingzi Cao Details: remove item from wishlist
@purchase_bp.route('/removewishlist', methods=['POST', 'GET'])
def removeWishList():
    if request.method == "POST":
        json_value = request.get_json()
        itemid = json_value["id"]
        userid = str(session.get('user_id'))
        deleteWishList(itemid, userid)
        return redirect("/purchase/wishlist")

# Author: Mingzi Cao Details: refresh item amount in wishlist front-end page and database
@purchase_bp.route('/refreshWishList', methods=['POST', 'GET'])
def refreshWishList():
    if request.method == "POST":

        json_value = request.get_json()
        itemid = str(json_value["id"])
        userid = str(session.get('user_id'))
        new_amount = json_value["new_amount"]
        cartlist_id = str(
            select("select wishlist_id from wishlist where item_id = '" + itemid + "' and buyer_id = '" + userid + "'")[
                0][0])
        if new_amount.isdigit() and int(new_amount) > 0:
            update("wishlist", "wishlist_id", cartlist_id, "amount", new_amount)
        return redirect("/purchase/cart")

# Author: Mingzi Cao Details: add single item in wishlist into cart
@purchase_bp.route('/WishList2Cart', methods=['POST', 'GET'])
def wishList2Cart():
    if request.method == "POST":

        json_value = request.get_json()
        itemid = str(json_value["id"])
        user_id = str(session.get('user_id'))
        amount = json_value["new_amount"]
        currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
        if amount.isdigit() and currentStock >= int(amount) > 0:
            cart_itemid = select(
                "select cartlist_id from cartlist where item_id =" + str(itemid) + " and buyer_id ='" + user_id + "'")
            if len(cart_itemid) <= 0:
                dic = {}
                dic["item_id"] = itemid
                dic["amount"] = amount
                dic["buyer_id"] = user_id
                insertCart("cartlist", dic)
            else:
                cart_itemid = str(cart_itemid[0][0])
                amountInCart = select("select amount from cartlist where cartlist_id =" + cart_itemid)[0][0]
                if int(amount) + int(amountInCart) <= currentStock:
                    update("cartlist", "cartlist_id", cart_itemid, "amount", int(amount) + int(amountInCart))
            deleteWishList(itemid, user_id)
        return redirect("/purchase/cart")

# Author: Mingzi Cao Details: add all items in wishlist into cart
@purchase_bp.route('/WishListAll2Cart', methods=['POST', 'GET'])
def wishListAll2Cart():
    if request.method == "POST":

        user_id = str(session.get('user_id'))
        userWishList = select("select item_id, amount from wishlist where buyer_id='" + user_id + "'")
        for temp in userWishList:
            itemid = str(temp[0])
            amount = int(temp[1])
            currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
            if currentStock >= int(amount) > 0:
                cart_itemid = select(
                    "select cartlist_id from cartlist where item_id =" + str(
                        itemid) + " and buyer_id ='" + user_id + "'")
                if len(cart_itemid) <= 0:
                    dic = {}
                    dic["item_id"] = itemid
                    dic["amount"] = amount
                    dic["buyer_id"] = user_id
                    insertCart("cartlist", dic)
                else:
                    cart_itemid = str(cart_itemid[0][0])
                    amountInCart = select("select amount from cartlist where cartlist_id =" + cart_itemid)[0][0]
                    if int(amount) + int(amountInCart) <= currentStock:
                        update("cartlist", "cartlist_id", cart_itemid, "amount", int(amount) + int(amountInCart))
                deleteWishList(itemid, user_id)
        return redirect("/purchase/cart")

# Author: Mingzi Cao Details: display all the order has made by this buyer
@purchase_bp.route('/orders')
def orders():
    user_info = str(session.get('user_info')) # get username to display in the page
    userid = str(session.get('user_id'))
    purchase_record = select(
        "select user.user_name, money_paid, paid_time, item.item_name from purchase INNER JOIN `user` ON "
        "`user`.user_id = purchase.buyer_id INNER JOIN item ON "
        "item.item_id=purchase.item_id WHERE purchase.buyer_id='" + userid + "'")
    return render_template('orders_purchase.html', size=len(purchase_record), user=user_info, purchase=purchase_record)


@purchase_bp.route('/credit')
def credit_card():
    user_info = str(session.get('user_info'))  # get username to display in the page
    month = [f"{i:02d}" for i in range(1, 13)]
    year = [str(datetime.now().year + i) for i in range(30)]
    message = ["Payment succeeded!!", "Payment failed! Please check your bank information again."]
    return render_template("credit_payment.html", months=month, length_month=len(month), years=year,
                           length_year=len(year), msg=message, user=user_info)


# Author Jialin Yang : This is a method of logout
@purchase_bp.route('/signout', methods=['GET', "POST"])
def signout():
    user_info = str(session.get('user_info'))
    session.pop('user_info')
    return redirect('/home/login')
