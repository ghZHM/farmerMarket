from flask import Flask, Blueprint, render_template, redirect, url_for, request, session
from models import *
import datetime

home_bp = Blueprint('home_bp', __name__,template_folder='templates',static_folder='static', static_url_path='assets');

#Author: Mingzi Cao Details:set login homepage
@home_bp.route('/')
def index():
    return redirect('/home/login')

#Author: Mingzi Cao Detail:user login page,can jump to other pages,unlawful input is handled
@home_bp.route('/login', methods=['GET', "POST"])  #default is post,but we need get for login,so special clarified
def login():
    if request.method == 'GET':
        return render_template('login.html')
    user = request.form.get('nm')#get input
    pwd = request.form.get('pw')
    sql = "SELECT verified from user where user_name=" + "'" + user + "'" + "and user_password=" + "'" + pwd + "'"# sql query
    result = select(sql)#use DataHelper.select to execute query
    n = str(result)#turn tuple into list so it can be seened visible(if sql is null, it will be null! len(n)is null)
    m = list(result)  # use it to judge whether sql result is null,len(m)=0
    if ((user == 'admin' and pwd == '123')or(len(m)!=0)):  # a hard-coded admin and use len to see if we input correctly according to the result of query
        if "1" in n:
            session['user_info'] = user  # record username
            userid = select("select user_id from user where user_name = '" + user + "'")
            userid = str(userid[0][0])
            #get user_id and store it # updated by Haoming, 13.03.2023
            usertype=select("select account_type from user where user_name = '" + user + "'")
            usertype=str(usertype[0][0])
            session['user_id'] = userid
            session['verified'] = "1"#deal with other string
            if usertype=="farmer":
                return redirect('/farmer/list')  # turn to success login and show the username(pass parameters between pages)
            if usertype == "buyer":
                return redirect('/purchase/purchase')  # turn to success login and show the username(pass parameters between pages)
            if usertype == "admin":
                return redirect('/admin/dashboard')
        if "0" in n:
            session['verified'] = "0"
            return render_template('login.html', msg='this account has not been verified !')  # not verified
    else:
        return render_template('login.html', msg='wrong!')#not found

#Author: Mingzi Cao Detail:forget password page,can jump to other pages,unlawful input is partly handled
@home_bp.route('/forgetpwd', methods=['GET', "POST"])
def forgetpwd():
    if request.method == 'GET':
        return render_template('forgetpwd.html')
    user = request.form.get('user')
    question=request.form.get("userquestion")
    answer=request.form.get("useranswer")
    if((len(user)!=0)and question and(len(question)!=0) and answer and(len(answer)!=0)):#because quetion and answer is radio,only use len()is not enough to judge whether its null
        sql = "SELECT user_password from user where user_name=" + "'" + user + "'" + "and user_question=" + "'" + question + "'" + "and user_answer=" + "'"+answer+"'"
        result=select(sql)
        n=list(result)
        if(len(n)!=0):#if found in database
            return n
        if(len(n)==0):#if not found
            return render_template('forgetpwd.html',msg='not found!')
    else:#some field is null,so tell the user to fill it
        return render_template('forgetpwd.html', msg='plz fill every blank')


#Author: Mingzi Cao Detail:index page,this is shown after success login and show the username by session
@home_bp.route('/user')
def user():
    user_info = session.get('user_info')#use get to find the success login usename
    user_verified=session.get('verified')
    u = select("select item_name, item_pic, item_price, item_stock from item order by item_name")
    if not user_info:#if it is null,redirect
        return redirect(url_for('home_bp.login'))
    else:
        return render_template("purchasePage.html", user=user_info, content=u, size=len(u))#if find, pass the username


#author: Vinit Mahajan Detail:Register Page Data Loading and validation
@home_bp.route('/register', methods=['GET', "POST"])#Vinit : added the /home/register instead of /register
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        dic={}#create a dic to get the input from front end and use it to insert into database
        dic["username"]=request.form.get("username")
        dic["first_name"]=request.form.get("firstname")
        dic["last_name"]=request.form.get("lastname")
        dic["user_email"]=request.form.get("email")
        dic["user_phone"]=request.form.get("phone")
        dic["account_type"]=request.form.get("usertype")
        dic["user_password"]=request.form.get("password")
        dic["user_question"]=request.form.get("userquestion")
        dic["user_answer"]=request.form.get("useranswer")
        if ((dic["account_type"]=="farmer")or (dic["account_type"]=="admin")):
            dic["verified"]="0"#this is for verifying the admin or farmer
        else:
            dic["verified"] ="1"#we dont need verify the buyer
        #also radion type need additional check
        if((len(dic["username"].strip())!=0)and(len(dic["first_name"].strip())!=0)and(len(dic["last_name"].strip())!=0)and(len(dic["user_email"])!=0)and(len(dic["user_phone"].strip())!=0)and dic["user_question"]and(len(dic["account_type"].strip())!=0)and(len(dic["user_password"].strip())!=0)and dic["user_question"] and(len(dic["user_question"].strip())!= 0) and (len(dic["user_answer"].strip())!= 0)):
            insert("user", dic)#if not null execute insert
            session["email"]=request.form.get("email")
            return redirect("/home/verify")
        else:#if its null,dont let it
            return render_template('register.html', msg='Wrong!')


#Mingzi Cao:verify after register
@home_bp.route('/verify', methods=['GET', "POST"])
def verify():
    email_info = session.get("email")
    #print(email_info)
    sql="SELECT user_Email from user ORDER BY user_id DESC LIMIT 1"#find the latest row
    last_line=select(sql)[0][0]#trun tuple in tuple to str
    #print("in database",last_line)
    if request.method == 'GET':
        session["vercode"] = send_email_get_code(str(email_info))
        session["start_time"]=datetime.datetime.now()#time after sending the email
        return render_template('emailverify.html')
    if request.method =='POST' :
        code=request.form.get("verify")
        ver_code=session.get("vercode")
        end_time=datetime.datetime.now()
        start_time=session.get("start_time")
        #print("time is:",end_time.minute-start_time.minute)
        if ((end_time.minute - start_time.minute) > 5):#input time is up
            code="0000"
        if ((ver_code != code)and(len(code)!=0)):#input wrong and time is up
            if(str(email_info)in last_line):#avoid mulit delete to the newly insert row
                deleteuser()
            return render_template("emailverify.html",msg="Email verification failed! PLZ regisrer again!")
        if (ver_code == code):
            return redirect("/home")



