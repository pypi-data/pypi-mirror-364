from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

class CreateDDLResponse(BaseModel):
    ddl: str
    ddl_path: Optional[str] = None

class FieldTransform(str, Enum):
    INITIALISM = "initialism"
    PHONETIC = "phonetic"
    SOUNDEX = "soundex"

class Field(BaseModel):
    table_name: str
    field_name: str
    field_transform: FieldTransform = None

class MatchEntityRequest(BaseModel):
    entity_name: str
    select_fields: List[Field]
    threshold: float = 0.8
    max_prefilter: int = 1000
