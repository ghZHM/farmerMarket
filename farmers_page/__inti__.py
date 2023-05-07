from flask import Flask

app = Flask(__name__)

from farmers_page.farmersPage import farmersPage_bp