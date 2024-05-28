# from playsound import playsound
from pydub import AudioSegment
import requests, json
import io
from fastapi.responses import JSONResponse
import joblib


user_id = "FWi1BS3D9DS9WUxrFUPyPKwNUgA3"
Authorization = "0c2fe6e05c934d1ea513af8fba346fd8"

#default values
default_voice = "s3://voice-cloning-zero-shot/a0fa25cc-5f42-4dd0-8a78-a950dd5297cd/original/manifest.json"
# "s3://voice-cloning-zero-shot/a59cb96d-bba8-4e24-81f2-e60b888a0275/charlottenarrativesaad/manifest.json"
#https://play.ht/app/voices to get the voice url
default_emotion = "male_happy"#male_sad,male_angry,male_surprised,male_fearful,male_disgust , same for female

#for more information on the api, visit
#https://docs.play.ht/reference/api-generate-audio

def create_voice_job(text = "Hi man how are you doing today?",
                      voice = default_voice, 
                      output_format = "mp3", 
                      voice_engine = "PlayHT2.0", 
                      speed = 0.86,
                      seed= 3,
                      emotion = "male_happy",
                      style_guidance = 10):

    url = "https://api.play.ht/api/v2/tts"

    payload = {
        "text": text,
        "voice": voice,
        "output_format": output_format,
        "voice_engine": voice_engine,
        "speed": speed,
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
    # Import the .pkl of the logistic regression model
    XGBmodel = joblib.load('routers/audio/pickles/xgboost_model.pkl')
    XGBvectorizer = joblib.load('routers/audio/pickles/XGBvectorizer.pkl')
    LRmodel = joblib.load('routers/audio/pickles/logistic_regression_model.pkl')
    LRvectorizer = joblib.load('routers/audio/pickles/LRvectorizer.pkl')
    # Try each model and return the emotion
    
    # Convert the text into counts
    X_test_counts = XGBvectorizer.transform([sentence])
    # Predict the emotion
    y_pred = XGBmodel.predict(X_test_counts)
    
    print("XGB", y_pred[0])
    
    # Convert the text into counts
    X_test_counts = LRvectorizer.transform([sentence])
    # Predict the emotion
    y_pred2 = LRmodel.predict(X_test_counts)
    print("LR", y_pred2[0])
    
    
    # map output to emotion
    # male_happy, male_sad, male_angry, male_surprised, male_fearful, male_disgust , same for female
    if y_pred2[0] == 0:
        # sad
        return "male_sad"
    if y_pred[0] == 2:
        # happy
        return "male_surprised"
    
    return "male_happy"
    
    
    # emotions = {
    # "They were always together and did everything together": "male_surprised",
    # "After a long journey, they finally found the treasure": "male_happy",
    # "the father of the first one died": "male_sad",
    # "They were so happy and celebrated their success": "male_happy",
    # "the second one was sad": "male_sad",
    # }
    # emotions = {
    #     "Lily and Tom had always dreamed of finding hidden treasure.": "male_surprised",
    #     "Inside, they found an old man who had been trapped for days.": "male_fearful",
    #     "He was weak and fearful.": "male_sad",
    #     "Returning home, they felt a mix of happiness and sadness, knowing they had not only found treasure but also helped someone in need.": "male_sad",
    # }

    # return emotions.get(sentence, "male_happy") #default emotion is neutral




def predict_environment_sound(sentence):
    # Import the .pkl of the logistic regression model
    LR = joblib.load('LR_weather_model.pkl')
    LRvectorizer = joblib.load('LR_weather_vectorizer.pkl')
    
    XGB = joblib.load('XGBweather_model.pkl')
    XGBvectorizer = joblib.load('XGBweather_vectorizer.pkl')
    
    # Try each model and return the environment sound
    # Convert the text into counts
    X_test_counts = LRvectorizer.transform([sentence])
    # Predict the environment sound
    y_pred = LR.predict(X_test_counts)
    
    print("LR", y_pred[0])
    
    # Convert the text into counts
    X_test_counts = XGBvectorizer.transform([sentence])
    # Predict the environment sound
    y_pred2 = XGB.predict(X_test_counts)
    print("XGB", y_pred2[0])
    
    # map output to environment sound
    # rain, storm , birds
    if y_pred2[0] == 2:
        # Rain
        return "rain"
    if y_pred[0] == 1:
        # Storm 
        return "storm"
    
    # Clear/ Default
    return "birds"
    
    
    
    #hard code for now
    # sounds = {
    # "They were always together and did everything together": "rain",
    # "After a long journey, they finally found the treasure": "fire",
    # "the father of the first one died": "rain",
    # "They were so happy and celebrated their success": "animals",
    # "the second one was sad": "birds"
    # }
    # sounds = {
    #     "Lily and Tom had always dreamed of finding hidden treasure.": "birds",
    #     "One sunny afternoon, while exploring an old forest, they found a mysterious map.": "animals",
    #     "He was weak and fearful.": "rain",
    #     "The old man was grateful and told them stories of his past adventures.": "fire",
    # }
    # return sounds.get(sentence, "birds")

def get_environment_sound(environment):
    sounds = {
    "rain": "routers/audio/env_sounds/rainy-day-in-town-with-birds-singing-194011.mp3",
    # "fire": "routers/audio/env_sounds/designed-fire-winds-swoosh-04-116788.mp3",
    "storm": "routers/audio/env_sounds/crickets-chirping_nature-sound-206330.mp3",
    "birds": "routers/audio/env_sounds/singing-club-of-birds_nature-sound-204240.mp3"
    }

    env_sound_file = sounds.get(environment, "routers/audio/env_sounds/singing-club-of-birds_nature-sound-204240.mp3")  # TEST HERE
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
