from pydantic import BaseModel
from typing import List, Optional
from .medication_model import Medication

class Beneficiary(BaseModel):
    name: str 
    doctor: str 
    medications: List[Medication] = []  