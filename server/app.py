class dummy():
    def __init__(self):
        pass

class Storage():
    def __init__(self):
        import importlib
        import ddr


        self.modules = dummy()
        self.modules.ddr = ddr.DDRWEB(self)
        self.modules.Thread = importlib.import_module("threading.Thread")
        self.modules.base64 = importlib.import_module("base64")
        self.threads = {}

        pass

    def refresh(self):
        self.importlib.reload(self.modules.ddr)
        pass

    def parse_image(self, image, imgid):
        thread = self.modules.Thread(target=self.modules.ddr.eval_image, args=(image, imgid,))
        thread.start()
        self.threads.update({imgid: thread})
        pass

    def check_eval_end(self, imgid):
        if imgid in self.threads:
            return False
        elif imgid in self.modules.ddr.database:
            return True
        else:
            return None

    def get_eval_result(self, imgid):
        return self.modules.ddr.database[imgid]
    
    def get_image(self, imgid):
        f = open(self.imagePath / (imgid + ".png"), "rb")
        rtn = self.modules.base64.b64encode(f.read())
        f.close()
        return rtn


        
from flask import *
from flask_compress import Compress
from hashlib import sha256
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
    if 'file' not in request.files:
        return Response({"status": 400, "message": "File not found"}, status=400, mimetype="application/json")
    elif request.files['file'].filename == '':
        return Response({"status": 400, "message": "File not found"}, status=400, mimetype="application/json")
    image = request.files['file']
    #Check extension
    if image.filename.split('.')[-1] not in ALLOWED_EXTENSIONS:
        return Response({"status": 400, "message": "File extension not allowed"}, status=400, mimetype="application/json")
    
    # get image as binary
    image_binary = image.read()
    imgid = sha256(image_binary).hexdigest()


    storage.parse_image(image_binary, imgid)
    return Response({"status": 200, "message": "OK", "data": {"id": imgid}}, status=200, mimetype="application/json")


@app.route('/ddr', methods=['GET'])
def return_tags(): 
    if 'id' not in request.args or 'id' not in request.json:
        return Response({"status": 400, "message": "ID not found"}, status=400, mimetype="application/json")
    try:
        imgid = request.args['id']
    except:
        imgid = request.json['id']
    if storage.check_eval_end(imgid) is None:
        return Response({"status": 500, "message": "Internal server error. Cannot find id in work and database."}, status=500, mimetype="application/json")
    elif storage.check_eval_end(imgid) is False:
        return Response({"status": 400, "message": "Image is still processing"}, status=400, mimetype="application/json")
    else:
        return Response({"status": 200, "message": "OK", "data": storage.get_eval_result(imgid), "image": storage.get_image(imgid)}, status=200, mimetype="application/json")

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