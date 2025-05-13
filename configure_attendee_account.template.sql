-- Configure Attendee Account

-- Create the warehouse
USE ROLE ACCOUNTADMIN;

ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'AWS_US';

CREATE OR REPLACE WAREHOUSE {{ env.EVENT_WAREHOUSE }}
WITH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;
  
use warehouse {{ env.EVENT_WAREHOUSE }};

----- Disable mandatory MFA -----
USE ROLE ACCOUNTADMIN;

CREATE DATABASE IF NOT EXISTS policy_db;
USE DATABASE policy_db;

CREATE SCHEMA IF NOT EXISTS policies;
USE SCHEMA policies;

CREATE AUTHENTICATION POLICY IF NOT EXISTS event_authentication_policy;

ALTER AUTHENTICATION POLICY event_authentication_policy SET
  MFA_ENROLLMENT=OPTIONAL
  CLIENT_TYPES = ('ALL')
  AUTHENTICATION_METHODS = ('ALL');

EXECUTE IMMEDIATE $$
    BEGIN
        ALTER ACCOUNT SET AUTHENTICATION POLICY event_authentication_policy;
    EXCEPTION
        WHEN STATEMENT_ERROR THEN
            RETURN SQLERRM;
    END;
$$
;
---------------------------------


-- Create the Attendee role if it does not exist
use role SECURITYADMIN;
create role if not exists {{ env.EVENT_ATTENDEE_ROLE }};

-- Ensure account admin can see what {{ env.EVENT_ATTENDEE_ROLE }} can see
grant role {{ env.EVENT_ATTENDEE_ROLE }} to role ACCOUNTADMIN;

-- Grant the necessary priviliges to that role.
use role ACCOUNTADMIN;
grant CREATE DATABASE on account to role {{ env.EVENT_ATTENDEE_ROLE }};
grant CREATE ROLE on account to role {{ env.EVENT_ATTENDEE_ROLE }};
grant CREATE WAREHOUSE on account to role {{ env.EVENT_ATTENDEE_ROLE }};
grant MANAGE GRANTS on account to role {{ env.EVENT_ATTENDEE_ROLE }};
grant CREATE INTEGRATION on account to role {{ env.EVENT_ATTENDEE_ROLE }};
grant CREATE APPLICATION PACKAGE on account to role {{ env.EVENT_ATTENDEE_ROLE }};
grant CREATE APPLICATION on account to role {{ env.EVENT_ATTENDEE_ROLE }};
grant IMPORT SHARE on account to role {{ env.EVENT_ATTENDEE_ROLE }};

-- Create the users
use role USERADMIN;
create user if not exists {{ env.EVENT_USER_NAME }}
    PASSWORD = '{{ env.EVENT_USER_PASSWORD }}'
    LOGIN_NAME = {{ env.EVENT_USER_NAME }}
    FIRST_NAME = '{{ env.EVENT_USER_FIRST_NAME }}'
    LAST_NAME = '{{ env.EVENT_USER_LAST_NAME }}'
    MUST_CHANGE_PASSWORD = false
    TYPE = PERSON;
create user if not exists {{ env.EVENT_ADMIN_NAME }}
    PASSWORD = '{{ env.EVENT_ADMIN_PASSWORD }}'
    LOGIN_NAME = {{ env.EVENT_ADMIN_NAME }}
    FIRST_NAME = '{{ env.EVENT_ADMIN_FIRST_NAME }}'
    LAST_NAME = '{{ env.EVENT_ADMIN_LAST_NAME }}'
    MUST_CHANGE_PASSWORD = false
    TYPE = PERSON;

-- Ensure the user can use the role and warehouse
use role SECURITYADMIN;
grant role {{ env.EVENT_ATTENDEE_ROLE }} to user {{ env.EVENT_USER_NAME }};
grant USAGE on warehouse {{ env.EVENT_WAREHOUSE }} to role {{ env.EVENT_ATTENDEE_ROLE }};

-- Ensure USER and ADMIN can use ACCOUNTADMIN role
grant role ACCOUNTADMIN to user {{ env.EVENT_USER_NAME }};
grant role ACCOUNTADMIN to user {{ env.EVENT_ADMIN_NAME }};

-- Alter the users to set default role and warehouse
use role USERADMIN;
alter user {{ env.EVENT_USER_NAME }} set
    DEFAULT_ROLE = {{ env.EVENT_ATTENDEE_ROLE }}
    DEFAULT_WAREHOUSE = {{ env.EVENT_WAREHOUSE }};
alter user {{ env.EVENT_ADMIN_NAME }} set
    DEFAULT_ROLE = ACCOUNTADMIN
    DEFAULT_WAREHOUSE = {{ env.EVENT_WAREHOUSE }};

-- Create the database and schemas using {{ env.EVENT_ATTENDEE_ROLE }}
use role {{ env.EVENT_ATTENDEE_ROLE }};

create database if not exists {{ env.EVENT_DATABASE }};
create schema if not exists {{ env.EVENT_DATABASE }}.{{ env.EVENT_SCHEMA }};
CREATE OR REPLACE SCHEMA {{ env.EVENT_DATABASE }}.CHEMBL29;
----------------------------------
-- Medical code extraction data --
----------------------------------
use database {{ env.EVENT_DATABASE }};
CREATE OR REPLACE FILE FORMAT CUSTOM_PDF;

-- Create external stage
CREATE OR REPLACE STAGE STAGING_REPORTS_DATA
URL='s3://sfquickstarts/sfguide_llm_assisted_medical_coding_extraction_for_healthcare_in_snowflake/'
    DIRECTORY = ( ENABLE = true )
    FILE_FORMAT = CUSTOM_PDF;

-- Create internal stage
CREATE OR REPLACE STAGE REPORTS_DATA 
DIRECTORY = (ENABLE = TRUE) 
FILE_FORMAT = CUSTOM_PDF
ENCRYPTION=(TYPE='SNOWFLAKE_SSE');

-- Copy files from an external to internal stage to make sure the files are server-side encrypted
COPY FILES INTO @REPORTS_DATA
FROM @STAGING_REPORTS_DATA;

ALTER STAGE REPORTS_DATA REFRESH;

--ensure internal marketplace datasets are available
--SHOW AVAILABLE LISTINGS;
SHOW AVAILABLE LISTINGS IS_ORGANIZATION = TRUE;
call SYSTEM$REQUEST_LISTING_AND_WAIT('GZTYZ1US953', 20);
call SYSTEM$REQUEST_LISTING_AND_WAIT('GZTYZ1US93L', 20);
call SYSTEM$REQUEST_LISTING_AND_WAIT('GZTYZ1US957', 20);


-------------------- CONTAINER RUNTIME -----------------------------------
use role ACCOUNTADMIN;

use database {{ env.EVENT_DATABASE }};

-- Create network rule and external access integration for pypi to allow users to pip install python packages within notebooks (on container runtimes)
CREATE NETWORK RULE IF NOT EXISTS pypi_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('pypi.org', 'pypi.python.org', 'pythonhosted.org',  'files.pythonhosted.org');

CREATE EXTERNAL ACCESS INTEGRATION IF NOT EXISTS pypi_access_integration
  ALLOWED_NETWORK_RULES = (pypi_network_rule)
  ENABLED = true;

create or replace network rule allow_all_rule
  TYPE = 'HOST_PORT'
  MODE= 'EGRESS'
  VALUE_LIST = ('0.0.0.0:443','0.0.0.0:80');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION allow_all_integration
  ALLOWED_NETWORK_RULES = (allow_all_rule)
  ENABLED = true;
  
GRANT USAGE ON INTEGRATION pypi_access_integration TO ROLE {{ env.EVENT_ATTENDEE_ROLE }};
GRANT USAGE ON INTEGRATION allow_all_integration TO ROLE {{ env.EVENT_ATTENDEE_ROLE }};

GRANT DATABASE ROLE SNOWFLAKE.PYPI_REPOSITORY_USER TO ROLE ATTENDEE_ROLE;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE ATTENDEE_ROLE;

-- Create a snowpark optimized virtual warehouse access of a virtual warehouse for newly created role
{# CREATE OR REPLACE WAREHOUSE E2E_ML_HOL_WAREHOUSE WITH
  WAREHOUSE_SIZE = 'MEDIUM';
  
GRANT USAGE ON WAREHOUSE E2E_ML_HOL_WAREHOUSE to ROLE {{ env.EVENT_ATTENDEE_ROLE }}; #}

-- Create compute pool to leverage GPUs

--DROP COMPUTE POOL IF EXISTS CP_GPU_NV_M_1;
--DROP COMPUTE POOL IF EXISTS CP_GPU_NV_S_4;
--DROP COMPUTE POOL IF EXISTS CP_GPU_NV_S_1_4;


--- Create a CPU POOL

CREATE COMPUTE POOL if not exists CPU_X64_S_1_3
  MIN_NODES = 1
  MAX_NODES = 3
  INSTANCE_FAMILY = CPU_X64_S
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 300;


-- Create a GPU compute pool for NVIDIA M-series, with 1 node, initially suspended
CREATE COMPUTE POOL if not exists CP_GPU_NV_M_1
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = GPU_NV_S
  INITIALLY_SUSPENDED = TRUE
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 300; 


-- Grant ownership of the compute pools to the newly created role ATTENDEE_ROLE
GRANT OWNERSHIP ON COMPUTE POOL CP_GPU_NV_M_1 TO ROLE ATTENDEE_ROLE; 
--GRANT OWNERSHIP ON COMPUTE POOL CP_GPU_NV_S_4 TO ROLE ATTENDEE_ROLE;
--GRANT OWNERSHIP ON COMPUTE POOL CP_GPU_NV_S_1_4 TO ROLE ATTENDEE_ROLE;
GRANT OWNERSHIP ON COMPUTE POOL CPU_X64_S_1_3 TO ROLE ATTENDEE_ROLE;

-- Grant ownership of database and schema to newly created role
GRANT OWNERSHIP ON DATABASE {{ env.EVENT_DATABASE }} TO ROLE {{ env.EVENT_ATTENDEE_ROLE }} COPY CURRENT GRANTS;
GRANT OWNERSHIP ON ALL SCHEMAS IN DATABASE {{ env.EVENT_DATABASE }}  TO ROLE {{ env.EVENT_ATTENDEE_ROLE }} COPY CURRENT GRANTS;

-- Grant usage back to ACCOUNTADMIN for visibility/usability
GRANT ALL ON DATABASE {{ env.EVENT_DATABASE }} TO ROLE ACCOUNTADMIN;
GRANT ALL ON ALL SCHEMAS IN DATABASE {{ env.EVENT_DATABASE }} TO ROLE ACCOUNTADMIN;

-- Create image repository
CREATE IMAGE REPOSITORY IF NOT EXISTS my_inference_images;
GRANT OWNERSHIP ON IMAGE REPOSITORY my_inference_images TO ROLE {{ env.EVENT_ATTENDEE_ROLE }};

GRANT CREATE SERVICE ON SCHEMA {{ env.EVENT_SCHEMA }} TO ROLE {{ env.EVENT_ATTENDEE_ROLE }};

-- Grant PRODUCER role privileges
GRANT CREATE DYNAMIC TABLE ON SCHEMA {{ env.EVENT_SCHEMA }} TO ROLE {{ env.EVENT_ATTENDEE_ROLE }};

-- Grant BIND SERVICE for Model Deployment to SPCS
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE ATTENDEE_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.PYPI_REPOSITORY_USER TO ROLE ATTENDEE_ROLE;

use role {{ env.EVENT_ATTENDEE_ROLE }};

CREATE OR REPLACE NETWORK RULE uk_gov_publishing_service 
MODE = EGRESS TYPE = HOST_PORT VALUE_LIST = ('assets.publishing.service.gov.uk');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION uk_gov_publishing_service
ALLOWED_NETWORK_RULES = (uk_gov_publishing_service)ENABLED = true;

CREATE OR REPLACE NETWORK RULE geoportal 
MODE = EGRESS TYPE = HOST_PORT VALUE_LIST = ('services1.arcgis.com');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION geoportal
ALLOWED_NETWORK_RULES = (geoportal)ENABLED = true;