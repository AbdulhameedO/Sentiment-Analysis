from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydub import AudioSegment

# import audio_manipulation.py
from .audio_manipulation import create_voice_job, audio_from_url, predict_emotion, predict_environment_sound,get_environment_sound, tokenize_text


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
    try:
        sentences = tokenize_text(text)
        merged_audio = AudioSegment.silent(duration=0)
        for sentence in sentences:
            emotion = predict_emotion(sentence)
            env = predict_environment_sound(sentence)
            env_sound = get_environment_sound(env)
            print(f"Generating audio for sentence: {sentence} with emotion: {emotion}")
            audio_url = create_voice_job(sentence, emotion=emotion)
            audio = audio_from_url(audio_url)
            combined = audio.overlay(env_sound, position=0)
            merged_audio += combined
        merged_audio.export("files/generated_audio.mp3", format="mp3")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "text to speech successful"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "text to speech failed"})
    