import unicodedata
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from uuid import UUID, uuid4
from datetime import datetime
import unicodedata


class Permission(BaseModel):
    name: str


class Group(BaseModel):
    name: str


class keycloakUserAbstract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: EmailStr
    password: str
    last_login: Optional[datetime] = None
    email_verified: bool = False

    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    is_staff: bool = False
    is_active: bool = True
    date_joined: datetime = Field(default_factory=datetime.utcnow)

    is_superuser: bool = False
    realm_name: Optional[str] = None

    permissions: List[Permission] = []
    groups: List[Group] = []

    _password: Optional[str] = None  # solo si implementas lógica de hash manualmente

    def get_username(self) -> str:
        return self.username

    @field_validator("username", mode="before")
    def normalize_username(cls, v):
        return unicodedata.normalize("NFKC", v)

    @field_validator("email", mode="before")
    def normalize_email(cls, v):
        return v.lower()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name or ""

    def get_all_permissions(self) -> set[str]:
        return {perm.name for perm in self.permissions}

    def has_perm(self, perm: str) -> bool:
        if self.is_active and self.is_superuser:
            return True
        return perm in self.get_all_permissions()

    def has_perms(self, perms: List[str]) -> bool:
        if self.is_active and self.is_superuser:
            return True
        return all(self.has_perm(p) for p in perms)

    def has_module_perms(self, app_label: str) -> bool:
        if self.is_active and self.is_superuser:
            return True
        return any(perm.startswith(f"{app_label}.") for perm in self.get_all_permissions())

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_authenticated(self) -> bool:
        return True

    def __str__(self) -> str:
        return str(self.id)


class User(keycloakUserAbstract):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
