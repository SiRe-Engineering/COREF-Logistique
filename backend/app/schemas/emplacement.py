from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EmplacementBase(BaseModel):
    nom: str = Field(min_length=1, max_length=150)
    type: str = Field(min_length=2, max_length=30)
    parent_id: int | None = None
    allee: str | None = Field(default=None, max_length=5)
    rack: str | None = Field(default=None, max_length=10)
    etage: int | None = Field(default=None, ge=1, le=99)
    case: str | None = Field(default=None, max_length=5)

    @model_validator(mode="after")
    def valider_coordonnees(self):
        if self.type.upper() == "CASE_MOULE":
            manquants = [
                nom
                for nom, valeur in {
                    "allée": self.allee,
                    "rack": self.rack,
                    "étage": self.etage,
                    "case": self.case,
                }.items()
                if valeur in (None, "")
            ]
            if manquants:
                raise ValueError(
                    "Une case de moule nécessite : " + ", ".join(manquants)
                )
        return self


class EmplacementCreate(EmplacementBase):
    code: str | None = Field(default=None, max_length=40)


class EmplacementUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=150)
    type: str | None = Field(default=None, min_length=2, max_length=30)
    parent_id: int | None = None
    allee: str | None = Field(default=None, max_length=5)
    rack: str | None = Field(default=None, max_length=10)
    etage: int | None = Field(default=None, ge=1, le=99)
    case: str | None = Field(default=None, max_length=5)
    actif: bool | None = None


class EmplacementRead(EmplacementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    actif: bool
    date_creation: datetime
    date_modification: datetime
    enfants: list["EmplacementRead"] = []
