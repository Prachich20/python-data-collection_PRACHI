from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    external_account_id: Optional[str]

class Farmer(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint('user_id', 'year', 'season'),
        )

    id: int = Field(default=None, primary_key=True)
    year: int
    season: str
    is_crop: bool
    is_tillage: bool
    user_id: int = Field(default=None, foreign_key="user.id")    
    
    class Config:
        arbitrary_types_allowed = True


class Practice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    farmer_id: int = Field(default=None, foreign_key="farmer.id")
    tillage_depth: int = Field(default=None)
    tilage_type: str = Field(default=None)
    crop: str = Field(default=None)
    crop_variety: str = Field(default=None)    
