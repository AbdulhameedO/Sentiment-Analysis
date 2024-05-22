from playsound import playsound
from pydub import AudioSegment
import requests, json
import io


user_id = "FWi1BS3D9DS9WUxrFUPyPKwNUgA3"
Authorization = "0c2fe6e05c934d1ea513af8fba346fd8"

#default values
default_voice = "s3://voice-cloning-zero-shot/a0fa25cc-5f42-4dd0-8a78-a950dd5297cd/original/manifest.json"
# "s3://voice-cloning-zero-shot/a59cb96d-bba8-4e24-81f2-e60b888a0275/charlottenarrativesaad/manifest.json"
#https://play.ht/app/voices to get the voice url
default_emotion = "male_happy"#male_sad,male_angry,male_surprised,male_fearful,male_disgust , same for female
default_style_guidance = 10#int [0:30] 0 is neutral, 30 is very emotional

#for more information on the api, visit
#https://docs.play.ht/reference/api-generate-audio

def create_voice_job(text = "Hi man how are you doing today?",
                      voice = default_voice, 
                      output_format = "mp3", 
                      voice_engine = "PlayHT2.0", 
                      speed = 0.86,
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
        
    # print("Audio URL:", audio_url)
    return audio_url




def audio_from_url(url):

    response = requests.get(url)

    if response.status_code == 200:

        audio_content = AudioSegment.from_file(io.BytesIO(response.content))
        return audio_content

    else:
        print(f"Failed to download audio: {response.status_code} - {response.reason}")
        return None

# generated_audio_url = "https://peregrine-results.s3.amazonaws.com/pigeon/cEYth2Tj6KwHNcGlGb_0.mp3"
# filename = "generated_audio.mp3"

# audio = audio_from_url(generated_audio_url)

def predict_emotion(sentence):
    # emotions = {
    # "They were always together and did everything together": "male_surprised",
    # "After a long journey, they finally found the treasure": "male_happy",
    # "the father of the first one died": "male_sad",
    # "They were so happy and celebrated their success": "male_happy",
    # "the second one was sad": "male_sad",
    # }
    emotions = {
        "Lily and Tom had always dreamed of finding hidden treasure.": "male_surprised",
        "Inside, they found an old man who had been trapped for days.": "male_fearful",
        "He was weak and fearful.": "male_sad",
        "Returning home, they felt a mix of happiness and sadness, knowing they had not only found treasure but also helped someone in need.": "male_sad",
    }

    return emotions.get(sentence, "male_happy") #default emotion is neutral




def predict_environment_sound(sentence):
    #hard code for now
    # sounds = {
    # "They were always together and did everything together": "rain",
    # "After a long journey, they finally found the treasure": "fire",
    # "the father of the first one died": "rain",
    # "They were so happy and celebrated their success": "animals",
    # "the second one was sad": "birds"
    # }
    sounds = {
        "Lily and Tom had always dreamed of finding hidden treasure.": "birds",
        "One sunny afternoon, while exploring an old forest, they found a mysterious map.": "animals",
        "Inside, they found an old man who had been trapped for days.": "rain",
        "He was weak and fearful.": "rain",
        "The old man was grateful and told them stories of his past adventures.": "fire",
    }
    return sounds.get(sentence, "birds")

def get_environment_sound(environment):
    sounds = {
    "rain": "env_sounds/rainy-day-in-town-with-birds-singing-194011.mp3",
    "fire": "env_sounds/designed-fire-winds-swoosh-04-116788.mp3",
    "animals": "env_sounds/crickets-chirping_nature-sound-206330.mp3",
    "birds": "env_sounds/singing-club-of-birds_nature-sound-204240.mp3"
    }

    env_sound_file = sounds.get(environment, "singing-club-of-birds_nature-sound-204240.mp3")
    env_sound = AudioSegment.from_file(env_sound_file)

    #adjust volume
    env_sound = env_sound - 12

    return env_sound


# create every step separately and put output in list

emotions = []
[emotions.append(predict_emotion(sentence)) for sentence in sentences]
[print(sentence,"  :   ", emotion) for sentence, emotion in zip(sentences, emotions)]


environments = []
[environments.append(predict_environment_sound(sentence)) for sentence in sentences]
print(environments)


environment_sounds = []
[environment_sounds.append(get_environment_sound(env)) for env in environments]
print(environment_sounds)


audio_urls = []
[audio_urls.append(create_voice_job(sentence, emotion=emotion)) for sentence, emotion in zip(sentences, emotions)]
print(audio_urls)


audios = []
[audios.append(audio_from_url(url)) for url in audio_urls]
print(audios)


merged_audio = AudioSegment.silent(duration=0)

for audio, emotion, env_sound in zip(audios, emotions, environment_sounds):
    combined = audio.overlay(env_sound, position=0)
    merged_audio += combined

merged_audio.export("story.mp3", format="mp3")
playsound("story.mp3")