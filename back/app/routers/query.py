from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, aliased
from typing import List, Optional
from ..queryutils import Tokenizer, TokenType
from sqlalchemy import func, text
from sqlalchemy.sql.functions import func
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/query",
    tags=['Query']
)


@router.get("/")
def get_summary(db: Session = Depends(get_db), q: str = ""):
    print(q)
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(q)
    print("****************** tokens", tokens)
    operations = tokenizer.parse()
    print("************* operations",operations)
    patient_set = set()
    encounter_set = set()
    set_operator = ''
    for operation in operations:
        print(">>>>>>>>>>> operation", operation)
        temp_patient = set()
        temp_encounter = set()
        match operation[0]:
            case TokenType.AND:
                set_operator = 'and'
                continue 
            case TokenType.OR:
                set_operator = 'or'
                continue
            case TokenType.NOT:
                set_operator = 'not'
                continue
            case TokenType.EOF:
                continue
            case _ :
                if len(operation) == 2:
                    q = operate(operator=operation[0], term1=operation[1], db=db)
                if len(operation) == 3:
                    q = operate(operator=operation[0], term1=operation[1], term2=operation[2], db=db)
                our_list = list(q.all())
                temp_patient = {r[0] for r in our_list}
                temp_encounter = {r[1] for r in our_list}
        
        if set_operator:
            print('set_operator', set_operator)
            match set_operator:
                case "and":
                    patient_set = patient_set.intersection(temp_patient)
                    encounter_set = encounter_set.intersection(temp_encounter)
                case "or":
                    patient_set = patient_set.union(temp_patient)
                    encounter_set = encounter_set.union(temp_encounter)
                case "not":
                    patient_set = patient_set - temp_patient
                    encounter_set = encounter_set - temp_encounter
            set_operator = ''
        else :
            print('first parse')
            patient_set = patient_set.union(temp_patient)
            encounter_set = encounter_set.union(temp_encounter)
    print('>>> last patient set', patient_set)
    return {'patient_set': list(patient_set), 'encounter_set': list(encounter_set)}

def filter_query(key, op, value, model_class):
        ops = {TokenType.EQUAL: 'eq', 
                TokenType.NOT_EQUAL: 'ne', 
                TokenType.LT: 'lt',
                TokenType.GT: 'gt',
                TokenType.LE: 'le', 
                TokenType.GE: 'ge'}
        op = ops.get(op)
        column = getattr(model_class, key, None)
        try:
            attr = list(filter(
                lambda e: hasattr(column, e % op),
                ['%s', '%s_', '__%s__']
            ))[0] % op
        except:
            pass 
        
        if value == 'null':
            value = None
        filt = getattr(column, attr)(value)
        return filt 

def allen_operate(operator, term1, term2, db):
    of1 = aliased(models.ObservationFact, name='of1')
    of2 = aliased(models.ObservationFact, name='of2')
    q = db.query(of1.patient_num, of2.encounter_num, of1.start_date.label('start1'), func.coalesce(of1.start_date, of1.end_date).label('end1'), of2.start_date.label('start2'), func.coalesce(of2.start_date, of2.end_date).label('end2')).filter(of1.patient_num == of2.patient_num, of1.concept_cd == term1, of2.concept_cd == term2)
    match operator:
        case TokenType.TIME_BEFORE:
            q.filter(text("end1 < start2"))
        case TokenType.TIME_EQUALS:
            q.filter(text("start1 = start2"), text("end1 = end2"))
        case TokenType.TIME_FINISHES:
            q.filter(text("end1 = end2"), text("start2 < start1"))
        case TokenType.TIME_MEETS:
            q.filter(text("end1 = start2"))
        case TokenType.TIME_OVERLAPS:
            q.filter(text("start1 < start2"), text("end1 < end2"))
        case TokenType.TIME_STARTS:
            q.filter(text("start1 = start2"), text("end1 < end2"))
        case TokenType.TIME_WITHIN:
            q.filter(text("start2 < start1"), text("end1 < end2"))
    return q 

def recursive_operate(operator, term1, db):
    print("*********** recursive_operate runs", operator, term1)
    is_a = 'SNOMED:116680003'
    if operator == TokenType.DESCENDANTS:
        topq = db.query( models.ConceptRelationships.target.label('id'), models.ConceptRelationships.source.label('child_id') ).filter( models.ConceptRelationships.target == term1, models.ConceptRelationships.type_cd == is_a).cte('cte', recursive=True)
        bottomq = db.query(models.ConceptRelationships.target.label('id'), models.ConceptRelationships.source.label('child_id')).join(topq, models.ConceptRelationships.source == topq.c.id).filter(models.ConceptRelationships.type_cd == is_a)
        q = topq.union(bottomq)
    if operator == TokenType.ASCENDANTS:
        topq = db.query( models.ConceptRelationships.source.label('id'), models.ConceptRelationships.target.label('child_id') ).filter( models.ConceptRelationships.source == term1, models.ConceptRelationships.type_cd == is_a).cte('cte', recursive=True)
        bottomq = db.query(models.ConceptRelationships.source.label('id'), models.ConceptRelationships.target.label('child_id')).join(topq, models.ConceptRelationships.target == topq.c.id).filter(models.ConceptRelationships.type_cd == is_a)
        q = topq.union(bottomq)
    q = db.query(func.distinct(q.c.id))
    print('>>>>>>> qqq',q)
    r = db.query(models.ObservationFact.patient_num, models.ObservationFact.encounter_num).filter(models.ObservationFact.concept_cd.in_(q))
    print('>>>>>>> rrr', r)
    return r

def operate(operator, term1, term2=None, db=None):
    print('********** operate runs', operator, term1, term2)
    match operator:
        case TokenType.TERM:
            return db.query(models.ObservationFact.patient_num, models.ObservationFact.encounter_num).filter(models.ObservationFact.concept_cd == term1)
        case TokenType.LT | TokenType.GT | TokenType.LE | TokenType.GE | TokenType.EQUAL | TokenType.NOT_EQUAL:
            if type(term2) == str: 
                filt = filter_query(key="tval_char", op=operator, value=term2, model_class=models.ObservationFact)
                return db.query(models.ObservationFact.patient_num, models.ObservationFact.encounter_num).filter(models.ObservationFact.concept_cd == term1).filter(filt)
            else:
                filt = filter_query(key="nval_num", op=operator, value=term2, model_class=models.ObservationFact)
                return db.query(models.ObservationFact.patient_num, models.ObservationFact.encounter_num).filter(models.ObservationFact.concept_cd == term1).filter(filt)
        case TokenType.TIME_BEFORE | TokenType.TIME_EQUALS | TokenType.TIME_FINISHES | TokenType.TIME_MEETS | TokenType.TIME_OVERLAPS | TokenType.TIME_STARTS | TokenType.TIME_WITHIN:
            return allen_operate(operator, term1, term2, db)
        case TokenType.DESCENDANTS | TokenType.ASCENDANTS:
            return recursive_operate(operator, term1, db)


    