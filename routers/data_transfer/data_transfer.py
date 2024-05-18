from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse


router = APIRouter(
    prefix="/data-transfer",
    tags=["data-transfer"],
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
    "/download/{file_name}",
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
async def download_audio_file(filename: str):
    try:
        return FileResponse(f"files/{filename}", filename=filename)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "audio file not downloaded"})
