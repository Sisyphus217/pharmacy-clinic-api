from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from ..models.medication_model import Medication
from db.settings import SettingsDB
from bson import ObjectId
from typing import List
from typing import Optional

router = APIRouter(prefix='/medications', tags=['medications'])

settings = SettingsDB()

medications_collection = settings.COLLECTION_MED

@router.post("/", response_model=Medication)
async def create_medication(
    medication_id: int,
    name: str,
    dosage: str,
):
    existing_medication = await medications_collection.find_one({"id": medication_id})
    if existing_medication:
        raise HTTPException(status_code=409, detail="Medication with the given ID already exists")

    new_medication = Medication(id=medication_id, name=name, dosage=dosage)

    await medications_collection.insert_one(new_medication.dict())

    return JSONResponse(content=new_medication.dict(), status_code=201)

@router.get("/{medication_id}", response_model=Medication)
async def get_medication(medication_id: int):
    medication = await medications_collection.find_one({"id": medication_id})
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return JSONResponse(content=Medication(**medication).dict(), status_code=200)

@router.get("/", response_model=List[Medication])
async def get_all_medications():
    all_medications = []
    async for medication in medications_collection.find():
        all_medications.append(Medication(**medication))
    
    return JSONResponse(content=[medication.dict() for medication in all_medications], status_code=200)


@router.patch("/{medication_id}", response_model=Medication)
async def update_medication(
    medication_id: int,
    name: Optional[str] = None,
    dosage: Optional[str] = None,
):
    existing_medication = await medications_collection.find_one({"id": medication_id})

    if existing_medication is None:
        raise HTTPException(status_code=404, detail="Medication not found")

    update_data = {}
    
    if name is not None:
        update_data["name"] = name
    if dosage is not None:
        update_data["dosage"] = dosage

    if not update_data:
        return Medication(**existing_medication)

    await medications_collection.update_one({"id": medication_id}, {"$set": update_data})

    updated_medication = await medications_collection.find_one({"id": medication_id})

    return JSONResponse(content=Medication(**updated_medication).dict(), status_code=200)


@router.delete("/{medication_id}")
async def delete_medication(medication_id: int):
    existing_medication = await medications_collection.find_one({"id": medication_id})
    if existing_medication is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    result = await medications_collection.delete_one({"id": medication_id})
    if result.deleted_count == 1:
        return JSONResponse(content={"message": "Medication deleted successfully"}, status_code=204)
    else:
        raise HTTPException(status_code=500, detail="Failed to delete medication")
