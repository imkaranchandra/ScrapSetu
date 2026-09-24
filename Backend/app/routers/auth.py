from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, UserUpdate, TokenResponse
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pre-defined default accounts
DEFAULT_ACCOUNTS = [
    {
        "mobile": "9336864092",
        "password": "karancollector",
        "full_name": "Karan Chandra (Collector)",
        "role": "collector",
        "address": "Civil Lines",
        "city": "Lucknow"
    },
    {
        "mobile": "9936541942",
        "password": "ramrecyclers",
        "full_name": "Ram Recyclers",
        "role": "recycler",
        "business_name": "Ram Recycling Centre Pvt Ltd",
        "address": "Industrial Area, Phase 1",
        "city": "Lucknow"
    }
]

def seed_default_users(db: Session):
    """
    Seeds default specific collector and recycler credentials and updates passwords if changed.
    """
    for acc in DEFAULT_ACCOUNTS:
        existing = db.query(User).filter(User.mobile == acc["mobile"]).first()
        if not existing:
            user = User(
                mobile=acc["mobile"],
                password_hash=get_password_hash(acc["password"]),
                full_name=acc["full_name"],
                role=acc["role"],
                business_name=acc.get("business_name"),
                address=acc.get("address"),
                city=acc.get("city"),
                status="Active"
            )
            db.add(user)
        else:
            # Update password hash and details to match current credentials
            existing.password_hash = get_password_hash(acc["password"])
            existing.full_name = acc["full_name"]
            if acc.get("business_name"):
                existing.business_name = acc.get("business_name")
    db.commit()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with a specific mobile number and password.
    Role must be 'collector' or 'recycler'.
    """
    clean_mobile = user_in.mobile.strip()
    existing_user = db.query(User).filter(User.mobile == clean_mobile).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this mobile number already exists."
        )

    hashed_pw = get_password_hash(user_in.password)
    user = User(
        mobile=clean_mobile,
        password_hash=hashed_pw,
        full_name=user_in.full_name,
        role=user_in.role.lower(),
        business_name=user_in.business_name,
        address=user_in.address,
        city=user_in.city,
        status="Active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.mobile, "role": user.role, "id": user.id})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user with specific mobile and password.
    Rejects any unauthorized or incorrect credentials.
    """
    # Ensure default accounts are present
    seed_default_users(db)

    clean_mobile = credentials.mobile.strip()
    user = db.query(User).filter(User.mobile == clean_mobile).first()

    # Strict check: User must exist and password must match the hashed password
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile number or password."
        )

    access_token = create_access_token(data={"sub": user.mobile, "role": user.role, "id": user.id})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve profile details of the currently authenticated user.
    """
    return UserResponse.model_validate(current_user)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update profile details for the authenticated user.
    """
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.business_name is not None:
        current_user.business_name = update_data.business_name
    if update_data.address is not None:
        current_user.address = update_data.address
    if update_data.city is not None:
        current_user.city = update_data.city

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
