from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.schemas import CurrentUser, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=current_user.id, role=current_user.role)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: CurrentUser = Depends(get_current_user),
) -> UserResponse:
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view another user's profile",
        )
    return UserResponse(id=user_id, role="user" if user_id != current_user.id else current_user.role)
