
use role {{ env.EVENT_ATTENDEE_ROLE }};

CREATE SCHEMA IF NOT EXISTS {{ env.EVENT_DATABASE }}.{{ env.CORTEX_ANALYST_SCHEMA }};

CREATE STAGE IF NOT EXISTS {{ env.EVENT_DATABASE }}.{{ env.CORTEX_ANALYST_SCHEMA }}.cortex_analyst
  DIRECTORY = (enable = true)
  ENCRYPTION = (type = 'snowflake_sse');


PUT file:///{{ env.CI_PROJECT_DIR }}/dataops/event/analyst/semantic_model.yaml @{{ env.EVENT_DATABASE }}.{{ env.CORTEX_ANALYST_SCHEMA }}.cortex_analyst auto_compress = false overwrite = true;


ALTER STAGE {{ env.EVENT_DATABASE }}.{{ env.CORTEX_ANALYST_SCHEMA}}.cortex_analyst REFRESH;
