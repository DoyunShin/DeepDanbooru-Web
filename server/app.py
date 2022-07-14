class dummy():
    def __init__(self):
        pass

class Storage():
    def __init__(self):
        import importlib
        import ddr


        self.modules = dummy()
        self.modules.Thread = importlib.import_module("threading").Thread
        self.modules.base64 = importlib.import_module("base64")
        self.modules.ddr = ddr.DDRWEB(self)
        self.threads = {}

        pass

    def refresh(self):
        self.importlib.reload(self.modules.ddr)
        pass

    def parse_image(self, image, imgid):
        if self.check_eval_end(imgid) != None:
            return
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
        f = open(self.modules.ddr.imagePath / (imgid + ".png"), "rb")
        rtn = self.modules.base64.b64encode(f.read()).decode("utf-8")
        f.close()
        return rtn


        
from flask import *
from flask_compress import Compress
from hashlib import sha256
from flask_cors import CORS
import os
from PIL import Image
import io


storage = Storage()
compress = Compress()
app = Flask(__name__)
app.secret_key = os.urandom(12)
CORS(app)

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'webp', 'gif']

@app.route('/api/')
def main():
    #return 404 not found
    return {"status": 404, "message": "Not found"}, 404

@app.route('/api/ddr', methods=['POST'])
def get_images():
    if 'file' in request.files:
        pass
    elif request.files['file'].filename != '':
        pass
    # check request.json["file"]
    elif 'file' in request.json:
        pass
    else:
        return {"status": 400, "message": "File not found"}, 400

    image = request.files.get('file')
    if image.filename.split('.')[-1] not in ALLOWED_EXTENSIONS:
        return {"status": 400, "message": "File extension not allowed"}, 400

    image_binary = image.read()
    imgid = sha256(image_binary).hexdigest()

    timg = Image.open(io.BytesIO(image_binary))
    timg.save(storage.modules.ddr.imagePath / (imgid + ".png"), "PNG")
    storage.parse_image(io.BytesIO(image_binary), imgid)
    return {"status": 200, "message": "OK", "data": {"id": imgid}}, 200


@app.route('/api/ddr', methods=['GET'])
def return_tags(): 
    if ('id' not in request.args) and ('id' not in request.json):
        return {"status": 400, "message": "ID not found"}, 400
    try:
        imgid = request.args['id']
    except:
        try:
            imgid = request.json['id']
        except:
            return {"status": 400, "message": "ID not found"}, 400
    
    if storage.check_eval_end(imgid) is None:
        return {"status": 500, "message": "Internal server error. Cannot find id in work and database."}, 500
    elif storage.check_eval_end(imgid) is False:
        #102 Image is still processing
        return {"status": 102, "message": "Image is still processing"}, 102
    else:
        return {"status": 200, "message": "OK", "data": storage.get_eval_result(imgid), "image": storage.get_image(imgid)}, 200

    pass

@app.route('/api/module_reload', methods=['GET'])
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