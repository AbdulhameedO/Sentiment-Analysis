from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi import status
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordBearer

from dependencies.db.users import UsersDriver
from dependencies.models import users
from dependencies.token_handler import TokenHandler

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

users_driver = UsersDriver()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
token_handler = TokenHandler()

def get_user_info(user_id: str) -> users.UserInfo:
    return users_driver.get_user_by_id(user_id)

@router.get(
    "/emails/check",
    summary="check if email is available",
    description="check if email is available",
    response_class=PlainTextResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "email is available",
            "content": {
                "text/plain": {
                    "example": "email is available"
                },
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "email not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "email not found"
                    }
                }
            }
        }
    }
)
async def check_email(email: str):
    users_driver.handle_nonexistent_email(email)

    return PlainTextResponse("email is available", status_code=status.HTTP_200_OK)


@router.get(
    "/email/info/avatar",
    summary="get the the avatar of the email sent whether it is verified or not",
    responses={
        status.HTTP_200_OK: {
            "description": "login successfully",
            "content": {
                "application/json": {
                    "example": {
                        "avatar_url": "https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50?s=200",
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "wrong password or email is not verified",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "wrong email",
                    }
                }
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "email not found",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "email not found"
                        }
                    }
                }
            }
        }
    }
)
async def get_avatar(email: str) -> users.UserAvatar:
    users_driver.handle_nonexistent_email(email)
    return users.UserAvatar(**users_driver.get_user_by_email(email).dict())


@router.get(
    "/id/{user_id}/info",
    summary="get user information by id",
    description="get user information by id",
    responses={
        status.HTTP_200_OK: {
            "description": "get user information by id successfully",
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@gmail.com",
                        "firstname": "user",
                        "lastname": "user",
                        "avatar_url": "https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50?s=200",
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "user not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "user not found"
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "invalid user id",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "invalid user id"
                    }
                }
            }
        }
    }
)
async def get_user_by_id(user_id) -> users.UserInfo:
    return get_user_info(user_id)


@router.get(
    "/me/info",
    summary="get user information",
    description="get the user firstname, lastname and avatar",
)
async def get_info(token: Annotated[str, Depends(oauth2_scheme)]) -> users.UserInfo:
    user = token_handler.get_user(token)
    return get_user_info(user.id)

@router.put(
    "/me/edit",
    summary="edit user firstname, lastname, avatar",
    description="edit user information",
    response_class=PlainTextResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "list of followed users",
            "content": {
                "text/plain": {
                    "example": "User information updated successfully"
                },
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "invalid token",
            "content": {
                "text/plain": {
                    "example": {
                        "detail": "invalid token"
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "user not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "user not found"
                    }
                }
            }
        }
    })
async def edit_info(
        token: Annotated[str, Depends(oauth2_scheme)],
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        avatar_url: Optional[str] = None,
) -> PlainTextResponse:
    user = token_handler.get_user(token)
    users_driver.handle_nonexistent_user(user.id)
    users_driver.edit_info(user.id, firstname, lastname, avatar_url)
    return PlainTextResponse("User information updated successfully", status_code=status.HTTP_200_OK)
