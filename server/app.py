class dummy():
    def __init__(self):
        pass

class Storage():
    def __init__(self):
        import importlib
        from .ddr import DDRWEB
        self.importlib = importlib
        self.ddr = DDRWEB()
        self.modules = dummy()
        
        pass

    def refresh(self):
        self.importlib.reload(self.modules.ddr)
        pass

    def parse_image(self):
        pass

        
from flask import *
from flask_compress import Compress
import os

storage = Storage()
compress = Compress()
app = Flask(__name__)
app.secret_key = os.urandom(12)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

@app.route('/')
def main():
    #return 404 not found
    return Response({"status": 404, "message": "Not found"}, status=404, mimetype="application/json")

@app.route('/ddr', methods=['POST'])
def get_images():

    # Get files image
    # Multipath

    req = request.json
    
    

    status = 200
    message = "OK"
    return Response({"status": status, "message": message}, status=status, mimetype="application/json")

@app.route('/ddr', methods=['GET'])
def return_tags(): 
    pass

@app.route('/module_reload', methods=['GET'])
def module_reload():
    storage.refresh()
    return {"status": 200, "message": "Module reloaded"}

"""
POST로 이미지를 받고, id를 반환
GET으로 id를 받고, 참/거짓 반환
>> 참일시 이미지와 태그를 반환

POST
{
    "status": 200,
    "id": "SHA256"
}

GET
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