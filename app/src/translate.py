from deep_translator import GoogleTranslator
import src.variables as variables
import threading
import unidecode
import json
import time
import os

TRANSLATING = False

def Initialize():
    global Translator
    Languages = GetAvailableLanguages()
    LanugageIsValid = False
    for Language in Languages:
        if str(Languages[Language]) == str(variables.LANGUAGE):
            LanugageIsValid = True
            break
    if LanugageIsValid == False:
        variables.LANGUAGE = "en"
    Translator = GoogleTranslator(source="en", target=variables.LANGUAGE)

    if os.path.exists(f"{variables.PATH}cache/Translations/{variables.LANGUAGE}.json"):
        with open(f"{variables.PATH}cache/Translations/{variables.LANGUAGE}.json", "r") as f:
            try:
                File = json.load(f)
            except:
                File = {}
                with open(f"{variables.PATH}cache/Translations/{variables.LANGUAGE}.json", "w") as f:
                    json.dump({}, f, indent=4)
            variables.TRANSLATION_CACHE = File

def TranslateThread(Text):
    global TRANSLATING
    while TRANSLATING:
        time.sleep(0.1)
    TRANSLATING = True
    variables.POPUP = ["Translating...", 0, 0.5]
    Translation = Translator.translate(Text)
    variables.TRANSLATION_CACHE[Text] = unidecode.unidecode(Translation)
    variables.RENDER_FRAME = True
    TRANSLATING = False
    return Translation

def TranslationRequest(Text):
    threading.Thread(target=TranslateThread, args=(Text,), daemon=True).start()

def Translate(Text):
    if variables.LANGUAGE == "en":
        return Text
    elif Text in variables.TRANSLATION_CACHE:
        Translation = variables.TRANSLATION_CACHE[Text]
        return Translation
    elif TRANSLATING:
        return Text
    else:
        if Text != "":
            TranslationRequest(Text)
        return Text

def GetAvailableLanguages(ForceNewSearch=False):
    if ForceNewSearch == False and variables.AVAILABLE_LANGUAGES != {}:
        return variables.AVAILABLE_LANGUAGES
    Languages = GoogleTranslator().get_supported_languages(as_dict=True)
    FormattedLanguages = {}
    for Language in Languages:
        FormattedLanguage = ""
        for i, Part in enumerate(str(Language).split("(")):
            FormattedLanguage += ("(" if i > 0 else "") + Part.capitalize()
        FormattedLanguages[FormattedLanguage] = Languages[Language]
    variables.AVAILABLE_LANGUAGES = FormattedLanguages
    return FormattedLanguages

def SaveCache():
    if variables.LANGUAGE != "en":
        if os.path.exists(f"{variables.PATH}cache/Translations") == False:
            os.makedirs(f"{variables.PATH}cache/Translations")
        with open(f"{variables.PATH}cache/Translations/{variables.LANGUAGE}.json", "w") as f:
            json.dump(variables.TRANSLATION_CACHE, f, indent=4)