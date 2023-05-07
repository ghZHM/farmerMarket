#Importing all the blueprint(module) auth - Vinit
from flask import Flask, session
from home.home import home_bp
from farmers_page.farmersPage import farmersPage_bp
from purchase_page.purchasePage import purchase_bp
from admin_page.adminPage import adminPage_bp
from models import *

#Registration of the blueprints (part of architecture design auth - Vinit
app = Flask(__name__)
app.secret_key = 'QWERTYUIOP'#a global dictionary provided by Flask,use it to pass parameters
app.register_blueprint(home_bp, url_prefix='/home')
app.register_blueprint(farmersPage_bp, url_prefix='/farmer')
app.register_blueprint(purchase_bp, url_prefix='/purchase')
app.register_blueprint(adminPage_bp, url_prefix='/admin')