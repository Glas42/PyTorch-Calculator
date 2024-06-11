import src.variables as variables
import json

def EnsureFile(file:str):
    try:
        with open(file, "r") as f:
            try:
                json.load(f)
            except:
                with open(file, "w") as ff:
                    ff.write("{}")
    except:
        with open(file, "w") as f:
            f.write("{}")

def Get(category:str, name:str, value:any=None):
    try:
        EnsureFile(f"{variables.PATH}settings.json")
        with open(f"{variables.PATH}settings.json", "r") as f:
            settings = json.load(f)

        if settings[category][name] == None:
            return value
        
        return settings[category][name]
    except:
        if value != None:
            Set(category, name, value)
            return value
        else:
            pass

def Set(category:str, name:str, data:any):
    try:
        EnsureFile(f"{variables.PATH}settings.json")
        with open(f"{variables.PATH}settings.json", "r") as f:
            settings = json.load(f)

        if not category in settings:
            settings[category] = {}
            settings[category][name] = data

        if category in settings:
            settings[category][name] = data

        with open(f"{variables.PATH}settings.json", "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except:
        pass