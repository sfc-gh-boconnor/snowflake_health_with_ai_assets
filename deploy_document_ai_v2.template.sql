use role ACCOUNTADMIN;
GRANT DATABASE ROLE SNOWFLAKE.DOCUMENT_INTELLIGENCE_CREATOR TO ROLE {{ env.EVENT_ATTENDEE_ROLE }};


use role {{ env.EVENT_ATTENDEE_ROLE }};

CREATE SCHEMA IF NOT EXISTS {{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }};
GRANT CREATE snowflake.ml.document_intelligence on schema {{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }} to role {{ env.EVENT_ATTENDEE_ROLE }};
GRANT CREATE MODEL ON SCHEMA {{ env.EVENT_DATABASE }}.{{ env.EVENT_SCHEMA }} TO ROLE {{ env.EVENT_ATTENDEE_ROLE }};

CREATE STAGE if not exists {{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.consent_forms
  DIRECTORY = (enable = true)
  ENCRYPTION = (type = 'snowflake_sse');

CREATE STAGE if not exists  {{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.gp_notes
  DIRECTORY = (enable = true)
  ENCRYPTION = (type = 'snowflake_sse');


CREATE STAGE if not exists  {{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.research_papers
  DIRECTORY = (enable = true)
  ENCRYPTION = (type = 'snowflake_sse');

PUT file:///{{ env.CI_PROJECT_DIR }}/dataops/event/document_ai/consent_forms/*.pdf @{{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.consent_forms auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR }}/dataops/event/document_ai/gp_notes/*.jpeg @{{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.gp_notes auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR }}/dataops/event/document_ai/research_papers/*.pdf @{{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.research_papers auto_compress = false overwrite = true;


ALTER STAGE {{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.consent_forms REFRESH;

ALTER STAGE {{ env.EVENT_DATABASE }}.{{ env.DOCUMENT_AI_SCHEMA }}.gp_notes REFRESH;