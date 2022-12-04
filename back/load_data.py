
def load():
    import pandas as pd
    import numpy as np
    from pathlib import Path
    from app.config import settings
    from sqlalchemy import create_engine

    SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'


    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    root = Path("./data")

    patients = pd.read_csv(root /"patients.csv")
    patients_column = {"Id": "patient_num", 
                    "BIRTHDATE": "birth_date", 
                    "DEATHDATE": "death_date", 
                    "GENDER": "sex_cd", 
                    "RACE": "race_cd", 
                    "MARITAL": "marital_status_cd"}
    patients_type = {"patient_num": str, 
                    "birth_date": np.datetime64, 
                    "death_date": np.datetime64,
                    "sex_cd": str,
                    "race_cd": str,
                    "marital_status_cd": str}
    patients = patients.rename(patients_column, axis=1)[patients_column.values()]
    patients = patients.astype(patients_type)
    patients.race_cd = patients.race_cd.str.get(0)
    patients.loc[patients.marital_status_cd == 'nan', "marital_status_cd"] = "U"
    patients.to_sql(index=False, name="patient_dimension", con=engine, if_exists="append")

    locations = pd.read_csv(root /"organizations.csv")
    locations_column = {"Id": "location_cd", 
                    "NAME": "location"}
    locations_type = {"location_cd": str, 
                    "location": str}
    locations = locations.rename(locations_column, axis=1)[locations_column.values()]
    locations = locations.astype(locations_type)
    locations.to_sql(index=False, name="location", con=engine, if_exists="append")

    encounters = pd.read_csv(root /"encounters.csv")
    encounters_column = {"Id": "encounter_num", 
                    "START": "start_date", 
                    "STOP": "end_date", 
                    "PATIENT": "patient_num", 
                    "ORGANIZATION": "location_cd", 
                    }
    encounters_type = {"encounter_num": str, 
                    "start_date": np.datetime64, 
                    "end_date": np.datetime64,
                    "patient_num": str,
                    "location_cd": str,
                    }
    encounters = encounters.rename(encounters_column, axis=1)[encounters_column.values()]
    encounters = encounters.astype(encounters_type)
    encounters.to_sql(index=False, name="encounter_dimension", con=engine, if_exists="append")

    providers = pd.read_csv(root / "providers.csv")
    providers_column = {"Id": "provider_num", 
                    "NAME": "name_char", 
                    "SPECIALITY": "provider_blob", 
                    "ORGANIZATION": "department", 
                    }
    providers_type = {"provider_num": str, 
                    "name_char": str,
                    "provider_blob": str,
                    "department": str
                    }
    providers = providers.rename(providers_column, axis=1)[providers_column.values()]
    providers = providers.astype(providers_type)
    providers.to_sql(index=False, name="provider_dimension", con=engine, if_exists="append")

    snomed_concepts = pd.read_csv(root / "sct2_Concept_Full_US1000124_20220901.txt", delimiter="\t")
    snomed_concepts_column = {"id": "concept_num"}
    snomed_concepts_type = {"concept_num": str}
    snomed_concepts = snomed_concepts.rename(snomed_concepts_column, axis=1)[snomed_concepts_column.values()]
    snomed_concepts = snomed_concepts.astype(snomed_concepts_type)
    snomed_concepts["sourcesystem_cd"] = "SNOMED"
    snomed_concepts.concept_num = "SNOMED:" + snomed_concepts.concept_num
    snomed_concepts = snomed_concepts.drop_duplicates()
    snomed_concepts.to_sql(index=False, name="concept_dimension", con=engine, if_exists="append")

    snomed_relationships = pd.read_csv(root / "sct2_Relationship_Full_US1000124_20220901.txt", delimiter="\t")
    snomed_relationships_column = {"sourceId": "source",
                                "destinationId": "target", 
                                "typeId": "type_cd",
                                }
    snomed_relationships_type = {"source": str, 
                            "target": str, 
                            "type_cd": str}
    snomed_relationships = snomed_relationships.rename(snomed_relationships_column, axis=1)[snomed_relationships_column.values()]
    snomed_relationships = snomed_relationships.astype(snomed_relationships_type)
    snomed_relationships["sourcesystem_cd"] = "SNOMED"
    snomed_relationships.source = "SNOMED:" + snomed_relationships.source
    snomed_relationships.target = "SNOMED:" + snomed_relationships.target
    snomed_relationships.type_cd = "SNOMED:" + snomed_relationships.type_cd
    snomed_relationships = snomed_relationships.drop_duplicates()
    snomed_relationships.to_sql(index=False, name="concept_relationships", con=engine, if_exists="append")

    observations_paths = ["allergies.csv", "conditions.csv"]
    observations_column = { "START": "start_date", 
                        "STOP": "end_date", 
                        "PATIENT": "patient_num", 
                        "ENCOUNTER": "encounter_num", 
                        "CODE": "concept_cd"}
    observations_type = {"start_date": np.datetime64,
                        "end_date": np.datetime64, 
                        "patient_num": str,
                        "encounter_num": str,
                        "concept_cd": str,
                        }
    for observation_path in observations_paths:
        observations = pd.read_csv(root / observation_path, delimiter=",")
        observations = observations.rename(observations_column, axis=1)[observations_column.values()]
        observations = observations.astype(observations_type)
        observations.concept_cd = "SNOMED:" + observations.concept_cd
        observations['observation_id'] = (observations.patient_num + observations.encounter_num + observations.concept_cd + observations.start_date.astype(str))
        observations.to_sql(index=False, name="observation_fact", con=engine, if_exists="append")

    loinc = pd.read_csv(root / "Loinc.csv")
    loinc = loinc[['LOINC_NUM', 'COMPONENT', 'SHORTNAME', 'LONG_COMMON_NAME' , 'DisplayName', 'DefinitionDescription']]
    loinc = pd.melt(loinc, id_vars="LOINC_NUM").dropna()[['LOINC_NUM', 'value']]
    loinc = loinc.rename({"LOINC_NUM": "concept_num", "value": "concept_term"}, axis=1)

    loinc_concepts = loinc.concept_num.drop_duplicates()
    loinc_concepts = "LOINC:" + loinc_concepts
    loinc_concepts = loinc_concepts.to_frame()
    loinc_concepts['sourcesystem_cd'] = "LOINC"
    loinc_concepts.to_sql(index=False, name="concept_dimension", con=engine, if_exists="append")

    loinc["normalized_term"] = loinc.concept_term.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
    loinc = loinc.drop_duplicates(["concept_num", "normalized_term"])
    loinc = loinc.drop("normalized_term", axis=1)
    loinc['sourcesystem_cd'] = "LOINC"
    loinc.concept_num = "LOINC:" + loinc.concept_num
    loinc = loinc.loc[loinc.concept_term.str.len() <= 255, :]
    loinc.to_sql(index=False, name="concept_descriptions", con=engine, if_exists="append")

    observations = pd.read_csv(root / "observations.csv", delimiter=",")
    observations_column = { "DATE": "start_date",
                        "PATIENT": "patient_num", 
                        "ENCOUNTER": "encounter_num", 
                        "CODE": "concept_cd", 
                        "TYPE": "valtype_cd", 
                        "VALUE": "value_undefined", 
                        "UNITS": "unit"}
    observations_type = {"start_date": np.datetime64,
                        "patient_num": str,
                        "encounter_num": str,
                        "concept_cd": str,
                        "valtype_cd": str,
                        "value_undefined": str,
                        "unit": str
                        }
    observations = observations.rename(observations_column, axis=1)[observations_column.values()]
    observations = observations.astype(observations_type)
    observations.concept_cd = "LOINC:" + observations.concept_cd
    observations['observation_id'] = (observations.patient_num + observations.encounter_num + observations.concept_cd + observations.start_date.astype(str))
    observations.loc[observations.valtype_cd == "numeric", "valtype_cd"] = "N"
    observations.loc[observations.valtype_cd == "text", "valtype_cd"] = "T"
    observations['nval_num'] = observations.loc[observations.valtype_cd == "N", "value_undefined"].astype(float)
    observations['tval_char'] = observations.loc[observations.valtype_cd == "T", "value_undefined"].astype(str)
    observations = observations.drop("value_undefined", axis=1)
    observations = observations.loc[observations.concept_cd != "LOINC:QALY", :].reset_index(drop=True)
    observations = observations.loc[observations.concept_cd != "LOINC:DALY", :].reset_index(drop=True)
    observations = observations.loc[observations.concept_cd != "LOINC:QOLS", :].reset_index(drop=True)
    observations = observations.loc[observations.concept_cd != "LOINC:417181009", :].reset_index(drop=True)
    observations = observations.drop_duplicates("observation_id")
    observations.to_sql(index=False, name="observation_fact", con=engine, if_exists="append")

if __name__ == "__main__":
    try:
        load()
    except Exception as e:
        print(e)