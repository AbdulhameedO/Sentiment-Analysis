# from playsound import playsound
from pydub import AudioSegment
import requests, json
import io
from fastapi.responses import JSONResponse
import joblib

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

#implement random

import random

#get random number integer
rand_seed = random.randint(0, 500)

user_id = "FWi1BS3D9DS9WUxrFUPyPKwNUgA3"
Authorization = "0c2fe6e05c934d1ea513af8fba346fd8"

#default values
default_voice = "s3://voice-cloning-zero-shot/d82d246c-148b-457f-9668-37b789520891/adolfosaad/manifest.json"
# "s3://voice-cloning-zero-shot/a59cb96d-bba8-4e24-81f2-e60b888a0275/charlottenarrativesaad/manifest.json"
#https://play.ht/app/voices to get the voice url
default_emotion = "male_happy"#male_sad,male_angry,male_surprised,male_fearful,male_disgust , same for female

#for more information on the api, visit
#https://docs.play.ht/reference/api-generate-audio

def create_voice_job(text = "Hi",
                      voice = default_voice, 
                      output_format = "mp3", 
                      voice_engine = "PlayHT2.0", 
                      speed = 0.83,
                      seed= rand_seed,
                      temperature = 0.1,
                      emotion = "male_happy",
                      style_guidance = 10):

    url = "https://api.play.ht/api/v2/tts"

    payload = {
        "text": text,
        "voice": voice,
        "output_format": output_format,
        "voice_engine": voice_engine,
        "speed": speed,
        "temperature": temperature,
        "emotion": emotion,
        "seed": seed,
        "style_guidance": style_guidance
    }
    headers = {
        "accept": "text/event-stream",
        "content-type": "application/json",
        "AUTHORIZATION": Authorization,
        "X-USER-ID": user_id
    }

    response = requests.post(url, json=payload, headers=headers)

    response_lines = response.content.decode('utf-8').split("\n")

    audio_url = None

    for i, line in enumerate(response_lines):
        if line.startswith("event: completed"):
            data = json.loads(response_lines[i + 1].replace("data: ", ""))
            audio_url = data["url"]
            break

    if not audio_url:
        # raise response
        return JSONResponse(status_code=400, content={"detail": "url is None, Text is empty or pad response from api"})
        
    return audio_url




def audio_from_url(url):

    response = requests.get(url)

    if response.status_code == 200:

        audio_content = AudioSegment.from_file(io.BytesIO(response.content))
        return audio_content

    else:
        print(f"Failed to load audio: {response.status_code} - {response.reason}")
        return None


def predict_emotion(sentence):
    # XGBmodel = joblib.load('routers/audio/pickles/xgboost_model.pkl')
    # XGBvectorizer = joblib.load('routers/audio/pickles/XGBvectorizer.pkl')
    LRmodel = joblib.load('routers/audio/pickles/logistic_regression_model.pkl')
    LRvectorizer = joblib.load('routers/audio/pickles/LRvectorizer.pkl')
    
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    sentence = ' '.join([lemmatizer.lemmatize(word) for word in sentence.split() if word not in stop_words])
    
    
    # X_test_counts = XGBvectorizer.transform([sentence])
    # y_pred = XGBmodel.predict(X_test_counts)
    
    # print("XGB", y_pred[0])
    
    X_test_counts = LRvectorizer.transform([sentence])
    y_pred2 = LRmodel.predict(X_test_counts)
    
    
    
    # map output to emotion
    # male_happy, male_sad, male_angry, male_surprised, male_fearful, male_disgust , same for female
    if y_pred2[0] == 0:
        # sad
        print("LR sad")
        return "male_sad"
    if y_pred2[0] == 2:
        # happy
        print("LR surprised")
        return "male_surprised"
    
    print("LR happy")
    return "male_happy"
    


def predict_environment_sound(sentence):
    
    LR = joblib.load('routers/audio/pickles/LR_weather_model.pkl')
    LRvectorizer = joblib.load('routers/audio/pickles/LR_weather_vectorizer.pkl')
    
    # XGB = joblib.load('routers/audio/pickles/XGBweather_model.pkl')
    # XGBvectorizer = joblib.load('routers/audio/pickles/XGBweather_vectorizer.pkl')

    X_test_counts = LRvectorizer.transform([sentence])
    y_pred = LR.predict(X_test_counts)
    
    
    # X_test_counts = XGBvectorizer.transform([sentence])
    # y_pred2 = XGB.predict(X_test_counts)
    # print("XGB", y_pred2[0])
    
    # map output to environment sound
    # rain, storm , birds
    if y_pred[0] == 2:
        # Rain
        print("LR rain")
        return "rain"
    if y_pred[0] == 1:
        # Storm 
        print("LR storm")
        return "storm"
    
    print("LR birds")
    # Clear/ Default
    return "birds"
    

def get_environment_sound(environment):
    sounds = {
    "rain": "routers/audio/env_sounds/rain.mp3",
    "storm": "routers/audio/env_sounds/wind.mp3",
    "birds": "routers/audio/env_sounds/birds.mp3"
    }

    env_sound_file = sounds.get(environment, "routers/audio/env_sounds/birds.mp3")
    env_sound = AudioSegment.from_file(env_sound_file)
    #adjust volume
    env_sound = env_sound - 12

    return env_sound

def tokenize_text(text):
    #Split on . ! ? 
    tokenized = text.split(".")
    tokenized = [sentence.split("!") for sentence in tokenized]
    tokenized = [item for sublist in tokenized for item in sublist]
    tokenized = [sentence.split("?") for sentence in tokenized]
    tokenized = [item for sublist in tokenized for item in sublist]
    #remove empty string
    tokenized = list(filter(None, tokenized))
    return tokenized
