use role {{ env.EVENT_ATTENDEE_ROLE }};

create schema if not exists {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }};


create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.STREAMLIT_3;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/trial_suitability.py @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.STREAMLIT_3 auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.STREAMLIT_3 auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/config.toml @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.STREAMLIT_3/.streamlit auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/snowflake_logo_color_rgb.svg @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.STREAMLIT_3 auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/homepage/docs/stylesheets/extra.css @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.STREAMLIT_3 auto_compress = false overwrite = true;

CREATE OR REPLACE STREAMLIT {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.TRIAL_SUITABILITY
    ROOT_LOCATION = '@{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.STREAMLIT_3'
    MAIN_FILE = 'trial_suitability.py'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';

----------------------------------

create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/cortex_agent/app.py @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/cortex_agent/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/cortex_agent/config.toml @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT/.streamlit auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/snowflake_logo_color_rgb.svg @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/cortex_agent/styles.css @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT auto_compress = false overwrite = true;

CREATE OR REPLACE STREAMLIT {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT
    ROOT_LOCATION = '@{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.CORTEX_AGENT'
    MAIN_FILE = 'app.py'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';


-----snowpark streamlit streamlits-------

use role {{ env.EVENT_ATTENDEE_ROLE }};

create schema if not exists {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }};
create stage if not exists {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.EXAMPLE_STREAMLIT_STAGE;

PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/population_health/app.py @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.EXAMPLE_STREAMLIT_STAGE auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/population_health/environment.yml @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.EXAMPLE_STREAMLIT_STAGE auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/population_health/snowflake_logo_color_rgb.svg @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.EXAMPLE_STREAMLIT_STAGE auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/streamlit/population_health/config.toml @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.EXAMPLE_STREAMLIT_STAGE/.streamlit auto_compress = false overwrite = true;
PUT file:///{{ env.CI_PROJECT_DIR}}/dataops/event/homepage/docs/stylesheets/extra.css @{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.EXAMPLE_STREAMLIT_STAGE auto_compress = false overwrite = true;

CREATE OR REPLACE STREAMLIT {{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.POPULATION_HEALTH_BY_URBAN_EXTENTS
    ROOT_LOCATION = '@{{ env.EVENT_DATABASE }}.{{ env.STREAMLIT_SCHEMA }}.EXAMPLE_STREAMLIT_STAGE'
    MAIN_FILE = 'app.py'
    QUERY_WAREHOUSE = '{{ env.EVENT_WAREHOUSE }}';