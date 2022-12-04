from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.sql.functions import func
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/search",
    tags=['Search']
)


@router.get("/", response_model=List[schemas.Term])
def get_search(db: Session = Depends(get_db), limit: int = 10, terms: str = "", type: str = "all"):

    terms = terms.split(" ")
    q = db.query(models.ConceptDescriptions.concept_num, models.ConceptDescriptions.concept_term)
  
    for term in terms:
        q = q.filter(models.ConceptDescriptions.concept_term.ilike(f"%{term}%"))
    match type:
        case "snomed":
            q = q.filter(models.ConceptDescriptions.sourcesystem_cd == "SNOMED")
        case "loinc":
            q = q.filter(models.ConceptDescriptions.sourcesystem_cd == "LOINC")
  
    concepts = q.limit(limit).all()

    return concepts