from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

TypeCompte = Literal["TECHNIQUE", "METIER"]

RoleUtilisateur = Literal[
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
    "RESPONSABLE_LOGISTIQUE",
    "RESPONSABLE_PRODUCTION",
    "CHARGE_AFFAIRES",
    "UTILISATEUR_STANDARD",
    "CONSULTATION",
]


class UtilisateurCreate(BaseModel):
    prenom: str | None = Field(default=None, max_length=100)
    nom: str | None = Field(default=None, max_length=100)
    nom_complet: str | None = Field(default=None, max_length=150)
    email: EmailStr
    mot_de_passe: str = Field(min_length=10, max_length=128)
    role: RoleUtilisateur
    type_compte: TypeCompte = "METIER"
    entreprise: str = Field(default="COREF", min_length=1, max_length=150)
    fonction: str | None = Field(default=None, max_length=150)

    @model_validator(mode="after")
    def construire_nom_complet(self):
        if self.type_compte == "TECHNIQUE":
            if not self.nom_complet:
                raise ValueError(
                    "Le nom affiché est obligatoire pour un compte technique."
                )
        elif not self.prenom or not self.nom:
            raise ValueError(
                "Le prénom et le nom sont obligatoires pour un compte métier."
            )

        return self


class UtilisateurUpdate(BaseModel):
    prenom: str | None = Field(default=None, max_length=100)
    nom: str | None = Field(default=None, max_length=100)
    nom_complet: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    mot_de_passe: str | None = Field(
        default=None,
        min_length=10,
        max_length=128,
    )
    role: RoleUtilisateur | None = None
    type_compte: TypeCompte | None = None
    entreprise: str | None = Field(default=None, max_length=150)
    fonction: str | None = Field(default=None, max_length=150)
    actif: bool | None = None


class UtilisateurRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_complet: str
    prenom: str | None
    nom: str | None
    email: str
    role: str
    type_compte: str
    entreprise: str
    fonction: str | None
    actif: bool
    date_creation: datetime
    date_modification: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str


class LoginResponse(BaseModel):
    jeton: str
    utilisateur: UtilisateurRead
