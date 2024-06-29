from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base
from src.models.user import User as UserModel
from src.auth import encode_access_token, hash_password, verify_password
from src.schemas.user import User, Login, LoginResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def signup(signup_user: User, db: AsyncSession = Depends(Base.get_db)) -> int:
    """
    return signup user id
    """
    hashed_password = hash_password(plain_password=signup_user.password)
    new_user = UserModel(name=signup_user.name, password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user.id


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    response: Response, login_user: Login, db: AsyncSession = Depends(Base.get_db)
) -> LoginResponse:
    result = await db.execute(
        select(UserModel).where(UserModel.name == login_user.name)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="User not exists")

    if not verify_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    token_value = {"id": user.id, "name": user.name}
    access_token = encode_access_token(token_value, timedelta(hours=1))
    response.set_cookie(
        key="access_token", value=access_token.get("access_token"), httponly=True
    )

    return access_token
