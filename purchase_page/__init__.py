from flask import Flask

app = Flask(__name__)

from purchase_page.purchasePage import purchase_bp
