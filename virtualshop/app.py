from flask import Flask
from flask_restful import Api
from virtualshop.datamodel.shopConfig import ShopRegistration
from virtualshop.configuration.starterLog import Main
import os,sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__)
app.secret_key = 'kuberCart'
api = Api(app)
api.add_resource(ShopRegistration, '/shopRegistration')

if __name__ == '__main__':
    starterLog = Main()
    starterLog.main()
    app.run(debug=True, threaded=True)

