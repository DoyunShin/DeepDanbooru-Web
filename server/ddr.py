class dummy():
    def __init__(self):
        pass

class DDRWEB(Exception):
    def __init__(self):
        import importlib

        self.importlib = importlib
        self.modules = dummy()
        self.modules.sha256 = importlib.import_module("hashlib.sha256")
        self.modules.tf = importlib.import_module("tensorflow")
        self.modules.tf_io = importlib.import_module("tensorflow_io")
        self.modules.dd = importlib.import_module("deepdanbooru")
        self.modules.json = importlib.import_module("json")
        self.Path = importlib.import_module("pathlib.Path")


        self.config = dummy()
        self.data = dummy()

        

        self.load_config()
        self.load_data()
        self.load_database()
        pass

    def load_config(self):
        f = open("config.json", "r", encoding="utf-8")
        config = self.json.load(f)
        f.close()
        
        self.config.model_path = self.Path(config["model_path"])
        self.config.tag_path = self.Path(config["tag_path"])
        self.config.tag_general_path = self.Path(config["tag_general_path"])
        self.config.tag_character_path = self.Path(config["tag_character_path"])
        self.config.work_path = self.Path(config["work_path"])
        self.config.threshold = config["threshold"]

        self.check_config()
    
    def check_config(self):
        self.config.modelPath = self.Path(self.config.model_path)
        if self.config.modelPath.exists() == False: raise FileNotFoundError("Model not found")
        self.config.tagPath = self.Path(self.config.tag_path)
        if self.config.tagPath.exists() == False: raise FileNotFoundError("Tag file not found")
        self.config.tagGeneralPath = self.Path(self.config.tag_general_path)
        if self.config.tagGeneralPath.exists() == False: raise FileNotFoundError("Tag general file not found")
        self.config.tagCharacterPath = self.Path(self.config.tag_character_path)
        if self.config.tagCharacterPath.exists() == False: raise FileNotFoundError("Tag character file not found")

        self.workPath = self.Path(self.config.work_path)
        self.workPath.mkdir(parents=True, exist_ok=True)

        self.imagePath = self.workPath / "images"
        self.imagePath.mkdir(exist_ok=True)

        if self.config.threshold < 0 or self.config.threshold > 1: raise ValueError("threshold must be between 0 and 1")
        pass

    def load_database(self):
        dataPath = self.workPath / "database.json"
        if dataPath.exists():
            f = open(dataPath, "r", encoding="utf-8")
            self.database = self.json.load(f)
            f.close()
        else:
            f = open(dataPath, "w", encoding="utf-8")
            f.write("{}")
            f.close()
            self.database = {}

        pass

    def save_database(self):
        dataPath = self.workPath / "database.json"
        f = open(dataPath, "w", encoding="utf-8")
        self.json.dump(self.database, f, ensure_ascii=False, indent=4)
        f.close()
        pass

    def save_imgdata(self, image_name, sort_general, character, raiting):
        self.database.update({image_name: {"general": sort_general, "character": character, "raiting": raiting}})
        self.save_database()
        pass

    def load_data(self):
        # model
        self.data.model = self.modules.tf.keras.models.load_model(self.config.model, compile=False)

        # tags
        self.data.tags = dummy()
        with open(self.config.tag_path, "r", encoding="utf-8") as tags_stream:
            self.data.tags.all = [tag for tag in (tag.strip() for tag in tags_stream) if tag]
        with open(self.config.tag_general_path, "r", encoding="utf-8") as tags_stream:
            self.data.tags.general = [tag for tag in (tag.strip() for tag in tags_stream) if tag]
        with open(self.config.tag_character_path, "r", encoding="utf-8") as tags_stream:
            self.data.tags.character = [tag for tag in (tag.strip() for tag in tags_stream) if tag]




    def eval_image(self, image: bytes, imgid: str):
        #sha256(image).hexdigest()
        with open(self.imagePath / imgid+".png", "wb") as image_stream:
            image_stream.write(image)
        width = self.data.model.input_shape[2]
        height = self.data.model.input_shape[1]
        
        image = self.modules.dd.data.load_image_for_evaluate(image, width=width, height=height)
        image_shape = image.shape
        image = image.reshape((1, image_shape[0], image_shape[1], image_shape[2]))
        y = self.data.model.predict(image)[0]

        result_dict = {}

        for i, tag in enumerate(self.data.tags.all):
            result_dict[tag] = y[i]

        sort_general = {}
        sort_rating = {}
        sort_character = {}

        for tag in self.data.tags.all:
            if "rating:" in tag:
                sort_rating.update({tag: result_dict[tag]})
            elif tag in self.data.tags.character:
                sort_character.update({tag: result_dict[tag]})
            elif result_dict[tag] >= self.config.threshold:
                sort_general.update({tag: result_dict[tag]})
        
        sort_general = sorted(sort_general.items(), key=lambda x: x[1], reverse=True)
        sort_character = sorted(sort_character.items(), key=lambda x: x[1], reverse=True)
        sort_rating = sorted(sort_rating.items(), key=lambda x: x[1], reverse=True)
        #[('rating:safe', 1.5022916e-08), ('rating:explicit', 1.4161448e-08), ('rating:questionable', 1.4002417e-08)]
        #for tag, score in sort:
        #    yield tag, score
        raiting = sort_rating[0][0]
        character = sort_character[0][0]

        self.save_imgdata(imgid, sort_general, character, raiting)


        return sort_general, character, raiting
