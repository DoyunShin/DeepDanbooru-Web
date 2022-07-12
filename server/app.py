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

@app.route('/ddr', methods=['POST'])
def get_images():
    pass

@app.route('/ddr', methods=['GET'])
def return_tags(): 
    pass

"""
POST로 이미지를 받고, id를 반환
GET으로 id를 받고, 참/거짓 반환
>> 참일시 이미지와 태그를 반환
{
    "status": 200,
    "tags": {
        "general": [["girl", 0.5], ["catear", 0.3]],
        "character": "kaffu_chino",
        "rating": "safe"
    }
}
"""

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", threaded=True, port=8080)