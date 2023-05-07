from flask import Flask,Blueprint, request, redirect, render_template, session, url_for
import models
from models import *


adminPage_bp = Blueprint('adminPage_bp', __name__,template_folder='templates',static_folder='static', static_url_path='assets');

@adminPage_bp.route('/')
@adminPage_bp.route('/admin')



@adminPage_bp.route('/dashboard', methods=['POST', 'GET'])
def admin():
    if request.method=='GET':
        redirect("/admin/dashboard")
    allrow = select("select user_name,user_Email,user_phone,account_type,user_id  from user where verified=0")
    return render_template("account.html",allrow=allrow )

@adminPage_bp.route('/verified', methods=['POST', 'GET'])
def unique():
    if request.method == 'POST':
        user_id=request.form.get('user_name')
        models.update("user", "user_id",user_id, "verified", 1)
        return redirect('/admin/dashboard')







