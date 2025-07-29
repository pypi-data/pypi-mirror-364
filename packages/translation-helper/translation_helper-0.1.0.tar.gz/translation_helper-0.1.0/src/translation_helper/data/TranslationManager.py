import os
import json


class TManager:
    _instance = None
    path = ""
    mainLang = ""
    data = {}

    def __init__(self):
        print("Init called")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def loadData(self):
        for entry in os.listdir(self.path):
            entry_path = os.path.join(self.path, entry)
            if os.path.isdir(entry_path):
                file_path = os.path.join(entry_path, f"{entry}.json")
                try:
                    with open(file_path, "r", encoding="utf-8") as entry_data:
                        data_dict = json.load(entry_data)
                        self.data[entry] = data_dict
                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                    self.data[entry] = {}
                except json.JSONDecodeError:
                    print(f"Invalid JSON in file: {file_path}")
                    self.data[entry] = {}

        print(self.data)
        return self.data

    def getKeys(self):
        keys = []
        for key, value in self.data[self.mainLang].items():
            keys.append(key)

        return keys

    def saveData(self):
        for lang, value in self.data.items():
            file = os.path.join(self.path, lang, f"{lang}.json")
            print(file)
            with open(file, "w") as f:
                json.dump(value, f, indent=4)

    def addKey(self, key: str, val: str):
        self.data[self.mainLang][key] = val

    def removeKey(self, key: str):
        for lang, value in self.data.items():
            value.pop(key, None)
