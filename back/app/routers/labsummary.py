from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.sql.functions import func
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/summary",
    tags=['Lab summary']
)

@router.get("/")
def get_summary(db: Session = Depends(get_db), id: str = "", type: str = "lab"):
    try:
        valtype_cd = db.query(models.ObservationFact.valtype_cd).filter(models.ObservationFact.concept_cd == id).first()[0]
    except:
        return {}
    
    if valtype_cd == 'T':
        text_values = db.query(models.ObservationFact.tval_char).distinct().filter(models.ObservationFact.concept_cd == id).all()
        print(text_values)
        return {"value": {"min":'', "max":'', "mean":''}, "unit": [t[0] for t in text_values], 'type':'T'}

    elif valtype_cd == 'N':
        num_units = db.query(models.ObservationFact.unit).distinct().filter(models.ObservationFact.concept_cd == id).all()
        num_values = db.query(
            func.min(models.ObservationFact.nval_num).label("min"), 
            func.max(models.ObservationFact.nval_num).label("max"), 
            func.avg(models.ObservationFact.nval_num).label("mean")).distinct().filter(models.ObservationFact.concept_cd == id).first()
  
        num_values = dict(num_values)

        for k, v in num_values.items():
            num_values[k] = "{:.3f}".format(v)

        return {"value": num_values, "unit": [n[0] for n in num_units], 'type':'N'}

# http://localhost:8000/summary/?id=LOINC:39156-5&type=lab  # test numeric 
# http://localhost:8000/summary/?id=LOINC:72166-2&type=lab  # test text