from flask import Flask

app = Flask(__name__)

from admin_page.adminPage import adminPage_bp