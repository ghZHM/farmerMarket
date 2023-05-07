from flask import Blueprint, request, render_template, session, redirect, jsonify
import os
import models
from models import *
from datetime import datetime
import paypalrestsdk

purchase_bp = Blueprint('purchase_bp', __name__, template_folder='templates', static_folder='static',
                        static_url_path='assets')

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AUTUtWK1mV5ylaPEPs0XiYnsf98URaM5_lTeEBT-iiQDROsfWivLioaRhQffaO7fIcUr43oj_BHHjze9",
    "client_secret": "EHIWBWVXUl4QiXhfMwmmxeugX_MnzjxuqckzlOqnatqAw5V5YJ8b96iH5rCo6wXT5e7Qu9bCDBD8cNwr"
})

# Author: Haoming Zeng Details: select all the product from database and render the page
@purchase_bp.route('/purchase')
def purchase():
    goods = select(
        "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_stock > 0 order by item_name, item_price")

    # generate picture path
    imgPath = []
    prefixCategory = ["fruit","dairy","meat","seafood","vegetable","grain"]
    for temp in goods:
        if str(temp[5]).lower() in prefixCategory:
            imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
        else:
            imgPath.append("/static/default.jpg")

    return render_template("purchasePage.html", content=goods, size=len(goods), img=imgPath)

# Author: Haoming Zeng Details: select product from database based on category and render the page
@purchase_bp.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        category = str(request.form.get('category'))

        # perform query based on conditions
        if category == "all":
            goods = select(
                "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_stock > 0")
        else:
            goods = select(
                "select item_name, item_price, item_details, item_id, item_stock, item_categories from item where item_stock > 0 and item_categories ='" + category + "'")

        # generate image path based on name
        imgPath = []
        prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
        for temp in goods:
            if str(temp[5]).lower() in prefixCategory:
                imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
            else:
                imgPath.append("/static/default.jpg")

        return render_template("purchasePage.html", content=goods, size=len(goods), img=imgPath)

# Author: Haoming Zeng Details: select row from database via user_id and render the cart
@purchase_bp.route('/cart', methods=['POST', 'GET'])
def cart():
    if request.method == "GET":
        # to fix user_id
        # perform query based on user_id
        cartObjects = select(
            "select  cartlist.item_id, item.item_name, item.item_details, item.item_price, cartlist.amount, item.item_categories from cartlist INNER JOIN item ON cartlist.item_id = item.item_id where buyer_id ='" + "3" + "'")

        imgPath = []
        totalPrice = []
        sum = 0
        prefixCategory = ["fruit", "dairy", "meat", "seafood", "vegetable", "grain"]
        for temp in cartObjects :
            if str(temp[5]).lower() in prefixCategory:
                imgPath.append("/static/" + str(temp[5]).lower() + ".jpg")
            else:
                imgPath.append("/static/default.jpg")
            totalPrice.append(float(temp[3]) * int(temp[4]))
            sum += float(temp[3]) * int(temp[4]) # calculate the sum price of the cart

        return render_template("cart.html", img=imgPath, content=cartObjects, size=len(cartObjects), total=totalPrice,
                               sumPrice=sum)

# Author: Haoming Zeng Details: add or update the cart
@purchase_bp.route('/addCart', methods=['POST', 'GET'])
def addCart():
    if request.method == "POST":
        # get front-end input via ajax
        json_value = request.get_json()
        amount = json_value["amount"]
        itemid = json_value["id"]
        user_id="3" # to fix
        stock = select("select item_stock from item where item_id =" + str(itemid))

        if amount.isdigit() and 0 < int(amount) <= int(stock[0][0]):
            # search if the user has added the same product to cart
            cart_itemid = select("select cartlist_id from cartlist where item_id =" + str(itemid)+" and buyer_id ='"+user_id+"'")
            if len(cart_itemid)<=0:
                # create new row in cartlist
                dic = {}
                dic["item_id"] = itemid
                dic["amount"] = amount
                dic["buyer_id"] = user_id
                insertCart("cartlist", dic)
            else:
                # update on the previous row
                cart_itemid=str(cart_itemid[0][0])
                amountInCart = select("select amount from cartlist where cartlist_id =" + cart_itemid)[0][0]
                if int(amount) + int(amountInCart)<= int(stock[0][0]):
                    update("cartlist","cartlist_id",cart_itemid,"amount",int(amount) + int(amountInCart))

    return redirect("/purchase/cart")


# Author: Haoming Zeng Details: remove row from the cart
@purchase_bp.route('/removeCart', methods=['POST', 'GET'])
def removeCart():
    if request.method == "POST":
        json_value = request.get_json()
        itemid = json_value["id"]
        userid = "3" # tofix
        deleteCart(itemid,userid) # perform delete
        return redirect("/purchase/cart")

# Author: Haoming Zeng Details: refresh the cart page and database after modify
@purchase_bp.route('/refreshCart', methods=['POST', 'GET'])
def refreshCart():
    if request.method == "POST":

        json_value = request.get_json()
        itemid = str(json_value["id"])
        userid = "3" # tofix
        new_amount = json_value["new_amount"]
        cartlist_id = str(select("select cartlist_id from cartlist where item_id = '"+itemid+"' and buyer_id = '"+userid+"'")[0][0])
        currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
        if new_amount.isdigit() and 0<int(new_amount)<=currentStock:
            update("cartlist","cartlist_id",cartlist_id,"amount",new_amount)
        return redirect("/purchase/cart")


@purchase_bp.route('/payment', methods=['POST'])
def payment():
    user_id = "3"
    List = select("select item_id, amount from cartlist where buyer_id='" + user_id + "'")
    sum=0
    for temp in List:
        itemid = str(temp[0])
        amount = int(temp[1])
        currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
        if currentStock >= int(amount) > 0:
            paytime = str(datetime.now().strftime("%F %H:%M:%S"))
            address = "S3 7HG"  # address be fixed
            itemInfo = select("select farmer_id, item_price from item where item_id =" + str(itemid))
            dic = {}
            dic["item_id"] = itemid
            dic["farmer_id"] = str(itemInfo[0][0])
            dic["buyer_id"] = user_id
            dic["money_paid"] = amount * float(itemInfo[0][1])
            dic["address"] = address
            dic["paytime"] = paytime
            sum+=amount * float(itemInfo[0][1])
            insertPurchase(dic)
            update("item", "item_id", itemid, "item_stock", currentStock - amount)
            deleteCart(itemid, user_id)

    # for temp in cartObjects:
    #     totalPrice.append(float(temp[3]) * int(temp[4]))
    #     sum += float(temp[3]) * int(temp[4])

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
        print('Payment success!')
    else:
        print(payment.error)
    return jsonify({'paymentID': payment.id})



@purchase_bp.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    return jsonify({'success' : success})



# Author: Haoming Zeng Details: try to purchase all the items inside cart
@purchase_bp.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if request.method == "POST":

        user_id = "3"
        List = select("select item_id, amount from cartlist where buyer_id='"+user_id+"'")
        for temp in List:
            itemid=str(temp[0])
            amount = int(temp[1])
            currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
            if currentStock >= int(amount) > 0:
                paytime = str(datetime.now().strftime("%F %H:%M:%S"))
                address="S3 7HG" #  address be fixed
                itemInfo = select("select farmer_id, item_price from item where item_id ="+str(itemid))
                dic={}
                dic["item_id"]=itemid
                dic["farmer_id"]=str(itemInfo[0][0])
                dic["buyer_id"] = user_id
                dic["money_paid"] = amount* float(itemInfo[0][1])
                dic["address"]=address
                dic["paytime"]=paytime
                insertPurchase(dic)
                update("item","item_id",itemid,"item_stock",currentStock-amount)
                deleteCart(itemid, user_id)

    return redirect("/purchase/cart")

# Author: Haoming Zeng Details: query from database and render the front end page
@purchase_bp.route('/wishlist', methods=['POST', 'GET'])
def wishList():
    userid="3"
    if request.method == "GET":
        wishListObjects = select(
            "select wishlist.item_id, item.item_name, item.item_details, item.item_price, wishlist.amount, item.item_categories from wishlist INNER JOIN item ON wishlist.item_id = item.item_id where buyer_id ='" + userid+ "'")

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

        return render_template("wishList.html", img=imgPath, content=wishListObjects, size=len(wishListObjects), total=totalPrice,
                               sumPrice=sum)

@purchase_bp.route('/addwishlist', methods=['POST', 'GET'])
def addWishList():
    if request.method == "POST":
        json_value = request.get_json()
        # selectedGoodName = json_value["good"]
        amount = json_value["amount"]
        itemid = json_value["id"]
        user_id="3"
        # stock = select("select item_stock from item where item_id =" + str(itemid))

        if amount.isdigit() and 0 < int(amount):
            cart_itemid = select("select wishlist_id from wishlist where item_id =" + str(itemid)+" and buyer_id ='"+user_id+"'")
            if len(cart_itemid)<=0:
                dic = {}
                dic["item_id"] = itemid
                dic["amount"] = amount
                dic["user_id"] = user_id
                insertWishList(dic)
            else:
                cart_itemid=str(cart_itemid[0][0])
                amountInCart = select("select amount from wishlist where wishlist_id =" + cart_itemid)[0][0]
                update("wishlist","wishlist_id",cart_itemid,"amount",int(amount) + int(amountInCart))

    return redirect("/purchase/purchase")

@purchase_bp.route('/removewishlist', methods=['POST', 'GET'])
def removeWishList():
    if request.method == "POST":
        json_value = request.get_json()
        itemid = json_value["id"]
        userid = "3"
        deleteWishList(itemid,userid)
        return redirect("/purchase/wishlist")

@purchase_bp.route('/refreshWishList', methods=['POST', 'GET'])
def refreshWishList():
    if request.method == "POST":

        json_value = request.get_json()
        itemid = str(json_value["id"])
        userid = "3"
        new_amount = json_value["new_amount"]
        cartlist_id = str(select("select wishlist_id from wishlist where item_id = '"+itemid+"' and buyer_id = '"+userid+"'")[0][0])
        if new_amount.isdigit() and int(new_amount)>0:
            update("wishlist","wishlist_id",cartlist_id,"amount",new_amount)
        return redirect("/purchase/cart")

@purchase_bp.route('/WishList2Cart', methods=['POST', 'GET'])
def wishList2Cart():
    if request.method == "POST":

        json_value = request.get_json()
        itemid = str(json_value["id"])
        user_id = "3"
        amount = json_value["new_amount"]
        currentStock = int(select("select item_stock from item where item_id =" + str(itemid))[0][0])
        if amount.isdigit() and currentStock>=int(amount)>0:
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
            deleteWishList(itemid,user_id)
        return redirect("/purchase/cart")

@purchase_bp.route('/WishListAll2Cart', methods=['POST', 'GET'])
def wishListAll2Cart():
    if request.method == "POST":

        user_id = "3"
        userWishList = select("select item_id, amount from wishlist where buyer_id='"+user_id+"'")
        for temp in userWishList:
            itemid=str(temp[0])
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

@purchase_bp.route('/orders')
def orders():
    user_info = "idk"  # get username to display in the page
    userid = "3"
    purchase_record = select("select user.user_name, money_paid, paid_time, item.item_name from purchase INNER JOIN `user` ON "
                             "`user`.user_id = purchase.buyer_id INNER JOIN item ON "
                             "item.item_id=purchase.item_id WHERE purchase.buyer_id='" + userid + "'")
    return render_template('orders_purchase.html', size=len(purchase_record), user=user_info, purchase=purchase_record)


@purchase_bp.route('/credit')
def credit_card():
    month = [f"{i:02d}" for i in range(1, 13)]
    year = [str(datetime.now().year + i) for i in range(30)]
    message = ["Payment succeeded!!", "Payment failed! Please check your bank information again."]
    return render_template("credit_payment.html", months=month, length_month=len(month), years=year,
                           length_year=len(year), msg=message)
