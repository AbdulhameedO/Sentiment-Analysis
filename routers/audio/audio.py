from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydub import AudioSegment

# import audio_manipulation.py
from .audio_manipulation import create_voice_job, audio_from_url, predict_emotion, predict_environment_sound,get_environment_sound, tokenize_text, text_to_speech


router = APIRouter(
    prefix="/audio",
    tags=["audio"],
)

# Upload Text File
@router.post(
    "/upload",
    summary="upload text file",
    description="upload text file",
    responses={
        status.HTTP_200_OK: {
            "description": "text file uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "text file uploaded successfully"
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "text file not uploaded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "text file not uploaded"
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "text file not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "text file not found"
                    }
                }
            }
        }
    }
)
async def upload_text_file(file: UploadFile = File(...)):
    try:
        with open(f"files/{file.filename}", "wb") as f:
            f.write(file.file.read())
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "text file uploaded successfully"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "text file not uploaded"})
    
# Download Audio File
@router.get(
    "/download",
    summary="download audio file",
    description="download audio file",
    responses={
        status.HTTP_200_OK: {
            "description": "audio file downloaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "audio file downloaded successfully"
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "audio file not downloaded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "audio file not downloaded"
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "audio file not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "audio file not found"
                    }
                }
            }
        }
    }
)
async def download_audio_file(audio_url: str):
    try:
        audio = audio_from_url(audio_url)
        audio.export("files/generated_audio.mp3", format="mp3")
        return FileResponse("files/generated_audio.mp3")
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "audio file not downloaded"})
    

# Text to Speech
# First predict emotion and environment sound
# Then create voice job
# Then download audio file
@router.post(
    "/tts",
    summary="text to speech",
    description="text to speech",
    responses={
        status.HTTP_200_OK: {
            "description": "text to speech successful",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "text to speech successful"
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "text to speech failed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "text to speech failed"
                    }
                }
            }
        }
    }
)
async def text_to_speech(text: str):
    # create a dictionary of emotions to detect the most frequent emotion in the chapter
    # put male_happy, male_surprised, male_sad in the dictionary
    
    emotion_dict = {
        "male_happy": 0,
        "male_surprised": 0,
        "male_sad": 0
    }
    
    google = []

    try:
        sentences = tokenize_text(text)
        merged_audio = AudioSegment.silent(duration=0)
        for sentence in sentences:
            emotion = predict_emotion(sentence)
            emotion_dict[emotion[0]] += 1
            
            audio_url = create_voice_job(sentence, emotion=emotion)
            audio = audio_from_url(audio_url)
            combined = audio.overlay(env_sound, position=0)
            merged_audio += combined
            
            google.append((sentence,emotion[1],emotion[1]))
            
            
        # print(google)
        api_audio = text_to_speech(google)
        
        total_emotions = sum(emotion_dict.values()) - emotion_dict["male_happy"]
            
        # freq_emotion = max(emotion_dict, key=emotion_dict.get)
        # print(emotion_dict)
        
        # Check that happy is larger than 65% of the total emotions
        if emotion_dict["male_surprised"] > 0.65 * total_emotions:
            sound = "birds"
        elif emotion_dict["male_sad"] > 0.65 * total_emotions:
            sound = "wind"
        else:
            sound = "rain"
        print(sound)
    
        env_sound = get_environment_sound(sound)
        
        if len(merged_audio) < len(env_sound):
            env_sound = env_sound[:len(merged_audio)]
        else:
            env_sound = env_sound * (len(merged_audio) // len(env_sound))
            
        merged_audio = merged_audio.overlay(env_sound, position=0)   
        # api_audio = api_audio.overlay(env_sound,position=0)
        
        merged_audio.export("ad.mp3", format="mp3") 
        # api_audio.export("api.mp3", format="mp3")
        # merged_audio.export("generated_audio.mp3", format="mp3")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "text to speech successful"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "text to speech failed"})
    