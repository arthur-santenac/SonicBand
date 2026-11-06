"""Schémas Pydantic des requêtes et réponses de l'API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    nom: str = Field(min_length=1, max_length=255)
    email: EmailStr
    mot_de_passe: str = Field(min_length=8)

    @field_validator("nom")
    @classmethod
    def nom_non_vide(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le nom ne peut pas être vide.")
        return v

    @field_validator("mot_de_passe")
    @classmethod
    def longueur_bcrypt(cls, v: str) -> str:
        # bcrypt ne prend en compte que les 72 premiers octets.
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Le mot de passe ne doit pas dépasser 72 octets.")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    mot_de_passe: str = Field(min_length=1)


class UtilisateurOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_user: int
    nom_user: str
    email_user: str
    date_crea_user: datetime | None = None


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    utilisateur: UtilisateurOut


class GroupeIn(BaseModel):
    nom: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("nom")
    @classmethod
    def nom_non_vide(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le nom du groupe est obligatoire.")
        return v


class GroupeOut(BaseModel):
    id_grp: int
    nom_grp: str
    description_grp: str | None = None
    url_photo: str | None = None
    date_crea_grp: datetime | None = None
    nb_membres: int
    mon_role: str


class MembreOut(BaseModel):
    id_user: int
    nom_user: str
    email_user: str
    role: str
    date_rejoint: datetime | None = None


class InvitationEnvoyeeOut(BaseModel):
    """Invitation en attente, vue depuis le groupe (« Invitation envoyée »)."""

    id_invit: int
    email_invit: str
    nom_user: str | None = None
    date_invit: datetime | None = None


class MembresGroupeOut(BaseModel):
    membres: list[MembreOut]
    invitations: list[InvitationEnvoyeeOut]


class InvitationIn(BaseModel):
    email: EmailStr


class InvitationRecueOut(BaseModel):
    """Invitation affichée dans la boîte de réception de l'utilisateur invité."""

    id_invit: int
    id_grp: int
    nom_grp: str
    invite_par: str | None = None
    date_invit: datetime | None = None


class RepertoireIn(BaseModel):
    nom_rep: str = Field(min_length=1, max_length=255)

    @field_validator("nom_rep")
    @classmethod
    def nom_repertoire_non_vide(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Le nom du répertoire est obligatoire.")
        return value


class MorceauIn(BaseModel):
    titre_song: str = Field(min_length=1, max_length=255)
    compositeur: str | None = Field(default=None, max_length=255)
    lien_youtube: str | None = Field(default=None, max_length=255)
    url_img: str | None = Field(default=None, max_length=255)

    @field_validator("titre_song")
    @classmethod
    def titre_non_vide(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Le titre du morceau est obligatoire.")
        return value

    @field_validator("compositeur", "lien_youtube", "url_img")
    @classmethod
    def optional_values_trimmed(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class EquipementIn(BaseModel):
    nom_equipement: str = Field(min_length=1, max_length=255)

    @field_validator("nom_equipement")
    @classmethod
    def nom_non_vide(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Le nom de l'équipement est obligatoire.")
        return value


class EquipementOut(BaseModel):
    id_equipement: int
    nom_equipement: str
    proprietaire: str | None = None
    est_equipement_groupe: bool = False


class MorceauOut(BaseModel):
    id_song: int
    titre_song: str
    compositeur: str | None = None
    lien_youtube: str | None = None
    url_img: str | None = None
    position: int | None = None


class RepertoireOut(BaseModel):
    id_rep: int
    nom_rep: str
    morceaux: list[MorceauOut]