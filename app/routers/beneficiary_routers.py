from fastapi import APIRouter, Depends, HTTPException, Query,Path, Body
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from ..models.beneficiary_model import Beneficiary
from db.settings import SettingsDB
from bson import ObjectId
from typing import List
from ..models.medication_model import Medication

router = APIRouter(prefix='/beneficiaries', tags=['beneficiaries'])

settings = SettingsDB()

beneficiaries_collection = settings.COLLECTION_BEN
medications_collection = settings.COLLECTION_MED

@router.post("/")
async def create_beneficiary(
    name: str = Query(..., title="Patient's Name"),
    doctor: str = Query(..., title="Doctor's Name"),
    medication_ids: List[int] = Query(..., title="Comma-separated Medication IDs")
):
    beneficiary_id = str(ObjectId())

    beneficiary_data = {
        "_id": beneficiary_id,
        "name": name,
        "doctor": doctor,
        "medications": [{"id": med_id} for med_id in medication_ids]
    }

    settings.COLLECTION_BEN.insert_one(beneficiary_data)

    return JSONResponse(content={"beneficiary_id": beneficiary_id}, status_code=201)


@router.get("/{beneficiary_id}")
async def get_beneficiary_by_id(beneficiary_id: str = Path(..., title="Beneficiary ID")):
    beneficiary_data = await settings.COLLECTION_BEN.find_one({"_id": beneficiary_id})

    if not beneficiary_data:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    return JSONResponse(content=beneficiary_data, status_code=200)

@router.get("/", response_model=List[Beneficiary])
async def get_beneficiaries():
    beneficiaries_cursor = beneficiaries_collection.find()
    beneficiaries_list = []
    async for beneficiary in beneficiaries_cursor:
        beneficiaries_list.append(Beneficiary(**beneficiary))

    return beneficiaries_list

@router.patch("/{beneficiary_id}", response_model=Beneficiary)
async def update_beneficiary(
    beneficiary_id: str = Path(..., title="Beneficiary ID"),
    update_data: Beneficiary = Body(..., title="Updated Beneficiary Data")
):
    existing_beneficiary = await settings.COLLECTION_BEN.find_one({"_id": beneficiary_id})
    if not existing_beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    updated_beneficiary_data = {**existing_beneficiary, **update_data.dict()}
    await settings.COLLECTION_BEN.update_one({"_id": beneficiary_id}, {"$set": updated_beneficiary_data})

    return updated_beneficiary_data

@router.delete("/{beneficiary_id}", response_model=dict)
async def delete_beneficiary(beneficiary_id: str = Path(..., title="Beneficiary ID")):
    existing_beneficiary = await settings.COLLECTION_BEN.find_one({"_id": beneficiary_id})

    if not existing_beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    deletion_result = await settings.COLLECTION_BEN.delete_one({"_id": beneficiary_id})

    if deletion_result.deleted_count == 1:
        return JSONResponse(content={"message": "Beneficiary deleted successfully"}, status_code=204)
    else:
        raise HTTPException(status_code=409, detail="Deletion conflict. Unable to delete beneficiary.")