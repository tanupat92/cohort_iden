# Cohort Identification project

- combine ECL and Allen's interval algebra for query patient id and encounter id
- dbms project


## run on local
- `docker-compose up` 
- http://localhost:5173/


## data
- 1000 patients Synthea dataset
- snomed-ct and loinc for ontology 
    - to run properly, these 3 files need to be downloaded and copy into back/data 
        - sct2_Concept_Full* 
        - sct2_Description_Full*
        - sct2_Relationship_Full*
    

## how to use
1. search a term
    - if a term is lab only, users can see the summary of a lab test/ observation such as units, values, min, max, and mean. 
2. identify constraints

3. examples
    1. all patients that have BMI more than 40 but less or equal 45: 
        - `( { LOINC:39156-5 | Body mass index } > 40.0 ) and ( { LOINC:39156-5 | Body mass index } <= 45.0 )`

    2. all patients and visits that have necrotizing pneumonia or all descendants of this term in the ontology:
        - `( << { SNOMED:7063008 | Necrotizing pneumonia } )`

    3. all pregnant women that have DM type 2 after pregnancy and not before: 
        - `( { SNOMED:72892002 | Normal pregnancy (finding) } BEFORE { SNOMED:44054006 | Diabetes mellitus type 2 (disorder) } ) NOT ( { SNOMED:44054006 | Diabetes mellitus type 2 (disorder) } BEFORE { SNOMED:72892002 | Normal pregnancy (finding) })`
    
4. download patient id and encounter id in .csv 

## further work
- create duration and time point terms
- use ECL within conditions
- generate files that are friendly for analytics

