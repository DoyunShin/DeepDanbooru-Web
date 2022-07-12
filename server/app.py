class dummy():
    def __init__(self):
        pass

from flask import *
from flask_compress import Compress
import os

compress = Compress()
app = Flask(__name__)
app.secret_key = os.urandom(12)

@app.route('/')
def main():
    return "IT Works!"

@app.route('/image', methods=['POST'])
def put_image():
    pass



if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", threaded=True, port=8080)