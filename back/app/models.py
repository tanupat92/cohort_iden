from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, Text, UniqueConstraint, Numeric, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class PatientDimension(Base):
    __tablename__ = "patient_dimension"

    patient_num = Column(String(255), primary_key=True, nullable=False)
    vital_status = Column(String(3), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    death_date = Column(DateTime, nullable=True)
    sex_cd = Column(String(1), nullable=True)
    age_in_years = Column(Integer, nullable=True)
    race_cd = Column(String(1), nullable=True)
    marital_status_cd = Column(String(1), nullable=True)
    import_date = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))
    update_date = Column(DateTime, nullable=True)
    observations = relationship("ObservationFact")
    CheckConstraint("patient_dimension.death_date >= patient_dimension.birth_date", name="birth-death date constraint")
    CheckConstraint("patient_dimension.sex_cd IN ('M', 'F', NULL)")
    CheckConstraint("patient_dimension.marital_status_cd IN ('M', 'D', 'S', 'U', NULL)")
    CheckConstraint("patient_dimension.vital_status IN ('LIV', 'DEA', NULL)")

class EncounterDimension(Base):
    __tablename__ = "encounter_dimension"

    encounter_num = Column(String(255), primary_key=True, nullable=False)
    location_cd = Column(String(255), ForeignKey("location.location_cd", ondelete="CASCADE"), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    import_date = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))
    update_date = Column(DateTime, nullable=True)
    patient_num = Column(String(255), ForeignKey("patient_dimension.patient_num", ondelete="CASCADE" ),nullable=True)
    CheckConstraint("encounter_dimension.end_date >= encounter_dimension.start_date", "start end date constraint")
    observations = relationship("ObservationFact")

class Location(Base):
    __tablename__ = "location"

    location_cd = Column(String(255), primary_key=True, nullable=False)
    location = Column(String(255), nullable=False)
    update_date = Column(DateTime, nullable=True)
    encounters = relationship("EncounterDimension")

class ProviderDimension(Base):
    __tablename__ = "provider_dimension"

    provider_num = Column(String(255), primary_key=True, nullable=False)
    name_char = Column(String(255), nullable=True)
    provider_blob = Column(Text, nullable=True)
    department = Column(String(255), nullable=True)
    import_date = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))
    update_date = Column(DateTime, nullable=True)
    observations = relationship("ObservationFact")

class ConceptDimension(Base):
    __tablename__ = "concept_dimension"

    concept_num = Column(String(255), primary_key=True, nullable=False)
    name_char = Column(String(255), nullable=True)
    import_date = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))
    update_date = Column(DateTime, nullable=True)
    sourcesystem_cd = Column(String(255), nullable=True)
    observations = relationship("ObservationFact")
    descriptions = relationship("ConceptDescriptions")

class ConceptDescriptions(Base):
    __tablename__ = "concept_descriptions"

    concept_num = Column(String(255), ForeignKey("concept_dimension.concept_num", ondelete="CASCADE"), primary_key=True)
    concept_term = Column(String(255), primary_key=True)
    term_type = Column(String(255), nullable=True)
    import_date = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))
    update_date = Column(DateTime, nullable=True)
    sourcesystem_cd = Column(String(255), nullable=True)
 

class ConceptRelationships(Base):
    __tablename__ = "concept_relationships"

    source = Column(String(255), ForeignKey("concept_dimension.concept_num", ondelete="CASCADE"), primary_key=True)
    target = Column(String(255), ForeignKey("concept_dimension.concept_num", ondelete="CASCADE"), primary_key=True)
    type_cd = Column(String(255), ForeignKey("concept_dimension.concept_num", ondelete="CASCADE"), primary_key=True)
    import_date = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))
    update_date = Column(DateTime, nullable=True)
    sourcesystem_cd = Column(String(255), nullable=True)


class ObservationFact(Base):
    __tablename__ = "observation_fact"

    observation_id = Column(String(255), primary_key=True, nullable=False)
    patient_num = Column(String(255), ForeignKey("patient_dimension.patient_num", ondelete="CASCADE"))
    provider_num = Column(String(255), ForeignKey("provider_dimension.provider_num", ondelete="CASCADE"))
    encounter_num = Column(String(255), ForeignKey("encounter_dimension.encounter_num", ondelete="CASCADE"))
    concept_cd = Column(String(255), ForeignKey("concept_dimension.concept_num", ondelete="CASCADE"))
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    valtype_cd = Column(String(3), nullable=True)
    tval_char = Column(String(255), nullable=True)
    nval_num = Column(Numeric, nullable=True)
    unit = Column(String(255), nullable=True)
    import_date = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text('now()'))
    update_date = Column(DateTime, nullable=True)
    UniqueConstraint('observation_fact.patient_num', 
        'observation_fact.provider_num', 
        'observation_fact.encounter_num', 
        'observation_fact.concept_cd', 
        'observation_fact.star_date')
    CheckConstraint("observation_fact.end_date >= observation_fact.start_date", "start end date constraint")

