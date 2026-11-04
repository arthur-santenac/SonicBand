"""Routes d'authentification : inscription, connexion, utilisateur courant."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Invitation, Utilisateur
from backend.schemas import AuthOut, LoginIn, RegisterIn, UtilisateurOut
from backend.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def _find_by_email(db: Session, email: str) -> Utilisateur | None:
    return db.scalar(select(Utilisateur).where(func.lower(Utilisateur.email_user) == email.lower()))


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Utilisateur:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification requise.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized
    user = db.get(Utilisateur, user_id)
    if user is None:
        raise unauthorized
    return user


CurrentUser = Annotated[Utilisateur, Depends(get_current_user)]


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: DbSession) -> AuthOut:
    email = data.email.lower()
    if _find_by_email(db, email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Un compte existe déjà avec cet e-mail.")

    user = Utilisateur(
        nom_user=data.nom,
        email_user=email,
        mdp_hash=hash_password(data.mot_de_passe),
    )
    db.add(user)
    try:
        db.flush()
        # Rattache au nouveau compte les invitations reçues avant l'inscription.
        db.execute(
            update(Invitation)
            .where(Invitation.email_invit == email, Invitation.id_user.is_(None))
            .values(id_user=user.id_user)
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Un compte existe déjà avec cet e-mail.")
    db.refresh(user)
    return AuthOut(
        access_token=create_access_token(user.id_user),
        utilisateur=UtilisateurOut.model_validate(user),
    )


@router.post("/login", response_model=AuthOut)
def login(data: LoginIn, db: DbSession) -> AuthOut:
    user = _find_by_email(db, data.email)
    if user is None or not verify_password(data.mot_de_passe, user.mdp_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou mot de passe incorrect.")
    return AuthOut(
        access_token=create_access_token(user.id_user),
        utilisateur=UtilisateurOut.model_validate(user),
    )


@router.get("/me", response_model=UtilisateurOut)
def me(user: CurrentUser) -> Utilisateur:
    return user