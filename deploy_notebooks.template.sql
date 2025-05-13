use role {{ env.EVENT_ATTENDEE_ROLE }};

create schema if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }};


create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.PROCESS_DOCUMENTS;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/PROCESS_DOCUMENTS.ipynb @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.PROCESS_DOCUMENTS auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.PROCESS_DOCUMENTS auto_compress = false overwrite = true;

CREATE OR REPLACE NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.PROCESS_DOCUMENTS
    FROM '@{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.PROCESS_DOCUMENTS'
    MAIN_FILE = 'PROCESS_DOCUMENTS.ipynb'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';

ALTER NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.PROCESS_DOCUMENTS ADD LIVE VERSION FROM LAST;



create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.SIMULATE_DATA_WITH_CORTEX;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/SIMULATE_DATA_WITH_CORTEX.ipynb @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.SIMULATE_DATA_WITH_CORTEX auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.SIMULATE_DATA_WITH_CORTEX auto_compress = false overwrite = true;

CREATE OR REPLACE NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.SIMULATE_DATA_WITH_CORTEX
    FROM '@{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.SIMULATE_DATA_WITH_CORTEX'
    MAIN_FILE = 'SIMULATE_DATA_WITH_CORTEX.ipynb'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';

ALTER NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.SIMULATE_DATA_WITH_CORTEX ADD LIVE VERSION FROM LAST;


-- Medical Code Extraction Notebook
create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.MEDICAL_CODE_EXTRACTION;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/medical_code_extraction/medical_code_extraction.ipynb @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.MEDICAL_CODE_EXTRACTION auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/medical_code_extraction/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.MEDICAL_CODE_EXTRACTION auto_compress = false overwrite = true;

CREATE OR REPLACE NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.MEDICAL_CODE_EXTRACTION
    FROM '@{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.MEDICAL_CODE_EXTRACTION'
    MAIN_FILE = 'medical_code_extraction.ipynb'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';

ALTER NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.MEDICAL_CODE_EXTRACTION ADD LIVE VERSION FROM LAST;





-----drug discovery notebook--------


create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_3;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/drug_discovery_research/Snowflakeml_notebook_drugdiscovery.ipynb @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_3 auto_compress = false overwrite = true;
--PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/drug_discovery_research/ml_environment.yml @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_2 auto_compress = false overwrite = true;

CREATE OR REPLACE NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.AI_ML_FOR_DRUG_DISCOVERY
    FROM '@{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_3'
    MAIN_FILE = 'Snowflakeml_notebook_drugdiscovery.ipynb'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}'
    COMPUTE_POOL='CPU_X64_S_1_3'
    RUNTIME_NAME='SYSTEM$BASIC_RUNTIME';

ALTER NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.AI_ML_FOR_DRUG_DISCOVERY ADD LIVE VERSION FROM LAST;
ALTER NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.AI_ML_FOR_DRUG_DISCOVERY set external_access_integrations = ("pypi_access_integration", "allow_all_integration");


------snowpark and streamlit skills notebooks --------


use role {{ env.EVENT_ATTENDEE_ROLE }};

create schema if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }};
create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_1;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/analyse_data_snowpark_python.ipynb @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_1 auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_1 auto_compress = false overwrite = true;

CREATE OR REPLACE NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.ANALYSE_DATA_PYTHON
    FROM '@{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_1'
    MAIN_FILE = 'analyse_data_snowpark_python.ipynb'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';

ALTER NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.ANALYSE_DATA_PYTHON ADD LIVE VERSION FROM LAST;



create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_2;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/POPULATION_HEALTH_BY_URBAN_EXTENTS.ipynb @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_2 auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/notebooks/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_2 auto_compress = false overwrite = true;

CREATE OR REPLACE NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.POPULATION_HEALTH_BY_URBAN_EXTENTS
    FROM '@{{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.NOTEBOOK_2'
    MAIN_FILE = 'POPULATION_HEALTH_BY_URBAN_EXTENTS.ipynb'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';

ALTER NOTEBOOK {{ env.EVENT_DATABASE }}.{{ env.NOTEBOOKS_SCHEMA }}.POPULATION_HEALTH_BY_URBAN_EXTENTS ADD LIVE VERSION FROM LAST;
