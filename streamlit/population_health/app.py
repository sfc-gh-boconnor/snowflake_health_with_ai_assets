import json
import streamlit as st
import pandas as pd
import pydeck as pdk
import json
from snowflake.snowpark.types import *
from snowflake.snowpark.functions import *
from snowflake.snowpark.context import get_active_session
session = get_active_session()


st.set_page_config(layout="wide")
logo = 'snowflake_logo_color_rgb.svg'

#### this is referring to a file stored in the streamlit stage. 
### The streamlit stage is called EXAMPLE_STREAMLIT_STAGE.  you can add any file in side this stage which you can refer to in the code.
### The logo is also inside the same stage.


with open('extra.css') as ab:
    st.markdown(f"<style>{ab.read()}</style>", unsafe_allow_html=True)

    
st.logo(logo)


st.markdown('<h0black>POPULATION HEALTH BY </h0black><h0blue>URBAN EXTENTS</h0blue><BR>', unsafe_allow_html=True)

#population health converted to H3 in previous notebook
population_h3 = session.table('DEFAULT_SCHEMA.POPULATION_HEALTH_H3')


### urban extents as previously created in notebook
coverage_flattened = session.table('DEFAULT_SCHEMA.EXTENTS_WITH_H3')

population_by_area = coverage_flattened.join(population_h3,'H3','inner')

#### group by town to see metrics by town
urban_area_group = population_by_area.group_by('NAME1_TEXT').agg(sum('TOTAL_POPULATION').alias('TOTAL_POPULATION'),
                                            sum('CANCER').alias('CANCER'),
                                            sum('COPD').alias('COPD'),
                                            sum('ASTHMA').alias('ASTHMA'),
                                            sum('DIABETES').alias('DIABETES'),
                                            sum('HYPERTENSION').alias('HYPERTENSION'))

with st.container(height=300):
    st.markdown('<h1sub>TOP METRICS PER URBAN AREA</h1sub>',unsafe_allow_html=True)

    #### creating sorts and top 5 for each metric
    top_cancer = urban_area_group.with_column('CANCER',div0(col('CANCER'),col('TOTAL_POPULATION'))).select('CANCER','NAME1_TEXT').sort(col('CANCER').desc()).limit(5)
    top_copd = urban_area_group.with_column('COPD',div0(col('COPD'),col('TOTAL_POPULATION'))).sort(col('COPD').desc()).limit(5)
    top_asthma = urban_area_group.with_column('ASTHMA',div0(col('ASTHMA'),col('TOTAL_POPULATION'))).sort(col('ASTHMA').desc()).limit(5)
    top_hypertension = urban_area_group.with_column('HYPERTENSION',div0(col('HYPERTENSION'),col('TOTAL_POPULATION'))).sort(col('HYPERTENSION').desc()).limit(5)
    top_population = urban_area_group.sort(col('TOTAL_POPULATION').desc()).limit(3)
    top_diabetes = urban_area_group.with_column('DIABETES',div0(col('DIABETES'),col('TOTAL_POPULATION'))).sort(col('DIABETES').desc()).limit(5)

    ### adding bar charts to show top 3

    col1,col2,col3,col4,col5,col6 =st.columns(6)
    with col1:
        st.caption('TOTAL POPULATION')
        st.bar_chart(top_population.to_pandas(),x='NAME1_TEXT',y='TOTAL_POPULATION', color='#29B5E8',y_label='',x_label='', height=200)
    with col2:
        st.caption('CANCER')
        st.bar_chart(top_cancer.to_pandas(),x='NAME1_TEXT',y='CANCER', color='#29B5E8',y_label='',x_label='', height=200)
    with col3:
        st.caption('COPD')
        st.bar_chart(top_copd.to_pandas(),x='NAME1_TEXT',y='COPD', color='#29B5E8',y_label='',x_label='', height=200)
    with col4:
        st.caption('ASTHMA')
        st.bar_chart(top_asthma.to_pandas(),x='NAME1_TEXT',y='ASTHMA', color='#29B5E8',y_label='',x_label='', height=200)
    with col5:
        st.caption('DIABETES')
        st.bar_chart(top_diabetes.to_pandas(),x='NAME1_TEXT',y='DIABETES', color='#29B5E8',y_label='',x_label='', height=200)
    with col6:
        st.caption('HYPERTENSION')
        st.bar_chart(top_hypertension.to_pandas(),x='NAME1_TEXT',y='HYPERTENSION', color='#29B5E8',y_label='',x_label='', height=200)


with st.container(height=200):
    st.markdown('<h1sub>SELECT URBAN AREA, BODY WEIGHT AND GENDER</h1sub>',unsafe_allow_html=True)
    col1,col2,col3 = st.columns(3)
    with col1:
        urban_area = st.selectbox('Select Urban Area:', population_by_area.select('NAME1_TEXT').distinct().sort('NAME1_TEXT').dropna())
    with col2:
        body_weight = st.selectbox('Select Body Weight:', population_by_area.select('BODY_WEIGHT').distinct().dropna())
    with col3:
        SEX = st.selectbox('Select Gender:', population_by_area.select('SEX').distinct().dropna())

    df = population_by_area.filter((col('SEX')==SEX)&
                                  (col('BODY_WEIGHT')==body_weight)&
                                (col('NAME1_TEXT')==urban_area))
    #st.dataframe(df.drop('LAT',,height=250)

with st.container(height=150):
    st.markdown('<h1sub>TOTAL METRICS FOR SELECTION</h1sub>',unsafe_allow_html=True)
    pop_metrics = df.agg(sum('TOTAL_POPULATION').alias('TOTAL_POPULATION'),
      sum('CANCER').alias('CANCER'),
      sum('DIABETES').alias('DIABETES'),
      sum('COPD').alias('COPD'),
      sum('ASTHMA').alias('ASTHMA'),
      sum('HYPERTENSION').alias('HYPERTENSION')).to_pandas()

    col1,col2,col3,col4,col5,col6 = st.columns(6)
    with col1:
        st.metric('Total Population',pop_metrics.TOTAL_POPULATION)
    with col2:
        st.metric('Cancer Sufferers',pop_metrics.CANCER)
    with col3:
        st.metric('Diabetics',pop_metrics.DIABETES)
    with col4:
        st.metric('COPD Sufferers',pop_metrics.COPD)
    with col5:
        st.metric('Asthmatics',pop_metrics.ASTHMA)
    with col6:
        st.metric('Hypertension', pop_metrics.HYPERTENSION)


with st.container(height=600):
    st.markdown('<h1sub>LOCATION DETAILS</h1sub>',unsafe_allow_html=True)

    center = df.agg(avg('LAT'),avg('LON')).collect()

    LAT = center[0][0]
    LON = center[0][1]

    layer = pdk.Layer(
        "H3HexagonLayer",
        df.to_pandas(),
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        get_hexagon="H3",
        get_fill_color="[41 - TOTAL_POPULATION, 181-TOTAL_POPULATION, 232]",
        get_line_color=[1, 1, 1],
        line_width_min_pixels=1,
    )
    view_state = pdk.ViewState(latitude=LAT, longitude=LON, zoom=10, bearing=0, pitch=0)
    r = pdk.Deck(map_style=None,layers=[layer], initial_view_state=view_state, 
             tooltip={"html": "Total Population: {TOTAL_POPULATION}<BR>\
                                Total Cancer: {CANCER}<BR>\
                                Total Diabetes: {DIABETES}<BR>\
                                Total COPD: {COPD}<BR>\
                                Total Hypertension {HYPERTENSION}"})

    st.pydeck_chart(r)