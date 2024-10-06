import src.variables as variables
import json

def EnsureFile(File:str):
    try:
        with open(File, "r") as f:
            try:
                json.load(f)
            except:
                with open(File, "w") as ff:
                    ff.write("{}")
    except:
        with open(File, "w") as f:
            f.write("{}")

def Get(Category:str, Name:str, Value:any=None):
    try:
        EnsureFile(f"{variables.PATH}config/settings.json")
        with open(f"{variables.PATH}config/settings.json", "r") as f:
            Settings = json.load(f)

        if Settings[Category][Name] == None:
            return Value

        return Settings[Category][Name]
    except:
        if Value != None:
            Set(Category, Name, Value)
            return Value
        else:
            pass

def Set(Category:str, Name:str, Data:any):
    try:
        EnsureFile(f"{variables.PATH}config/settings.json")
        with open(f"{variables.PATH}config/settings.json", "r") as f:
            Settings = json.load(f)

        if not Category in Settings:
            Settings[Category] = {}
            Settings[Category][Name] = Data

        if Category in Settings:
            Settings[Category][Name] = Data

        with open(f"{variables.PATH}config/settings.json", "w") as f:
            f.truncate(0)
            json.dump(Settings, f, indent=6)
    except:
        pass