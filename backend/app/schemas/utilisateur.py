from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

RoleUtilisateur = Literal[
    "ADMINISTRATEUR",
    "RESPONSABLE_LOGISTIQUE",
    "RESPONSABLE_PRODUCTION",
    "CHARGE_AFFAIRES",
    "UTILISATEUR_STANDARD",
    "CONSULTATION",
]


class UtilisateurCreate(BaseModel):
    nom_complet: str = Field(min_length=2, max_length=150)
    email: EmailStr
    mot_de_passe: str = Field(min_length=10, max_length=128)
    role: RoleUtilisateur


class UtilisateurUpdate(BaseModel):
    nom_complet: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    email: EmailStr | None = None
    mot_de_passe: str | None = Field(
        default=None,
        min_length=10,
        max_length=128,
    )
    role: RoleUtilisateur | None = None
    actif: bool | None = None


class UtilisateurRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_complet: str
    email: str
    role: str
    actif: bool
    date_creation: datetime
    date_modification: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str


class LoginResponse(BaseModel):
    jeton: str
    utilisateur: UtilisateurRead
