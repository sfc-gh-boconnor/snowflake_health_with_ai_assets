# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F
from snowflake.snowpark import types as T
import pydeck as pdk
# Write directly to the app
st.title("Clinical Reports :pencil: ")
st.write(
    """### Synthetic Clinical Reports Viewer
    """
)

# Get the current credentials
session = get_active_session()


patients = session.table('HEALTH_DB.PROCESSED_DOCUMENTS.GENERATED_EVENTS').select('NHS_NUMBER')

with st.sidebar:
    patient_id = st.selectbox('Choose Patient:', patients)
    st.caption('0029959965')


patient_details = session.table('SYNTHETIC_POPULATION_DATA.PUBLIC.POPULATION_HEALTH_TABLE_OVERWEIGHT').filter(F.col('NHS_NUMBER')==patient_id).limit(1)

patient_details = patient_details.with_column('CANCER',F.when(F.col('CANCER')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('COPD',F.when(F.col('COPD')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('ASTHMA',F.when(F.col('ASTHMA')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('HYPERTENSION',F.when(F.col('HYPERTENSION')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('DIABETES',F.when(F.col('DIABETES')==1,F.lit('✅')).otherwise(F.lit('❌'))      )



patient_detailspd = patient_details.to_pandas()


#st.write(patient_details)

st.markdown('#### Patient information')
col1,col2 = st.columns(2)

with col1:

    st.markdown(f''' __NHS Number:__ {patient_detailspd.NHS_NUMBER.iloc[0]}''')

    st.markdown(f'''__First Name:__ {patient_detailspd.FIRST_NAME.iloc[0]}''')

    st.markdown(f'''__Last Name:__ {patient_detailspd.LAST_NAME.iloc[0]}''')

    st.markdown(f'''__Date of Birth:__ {patient_detailspd.DATE_OF_BIRTH.iloc[0]}''')

    st.markdown(f'''__Marital Status:__ {patient_detailspd.MARITAL_STATUS.iloc[0]}''')

    st.markdown(f'''__General Health:__ {patient_detailspd.GENERAL_HEALTH.iloc[0]}''')

    st.markdown(f'''__Occupation:__ {patient_detailspd.OCCUPATION.iloc[0]}''')

    st.markdown(f'''__Gender:__ {patient_detailspd.SEX.iloc[0]}''')

    st.markdown(f'''__Body Weight:__ {patient_detailspd.BODY_WEIGHT.iloc[0]}''')
    


with col2:
    st.markdown('###### Address Details:')
    st.markdown(f'''{patient_detailspd.ADDRESS_1.iloc[0]} {patient_detailspd.ADDRESS_2.iloc[0]}''')
    st.markdown(f'''{patient_detailspd.ADDRESS_3.iloc[0]}''')
    st.markdown(f'''{patient_detailspd.ADDRESS_5.iloc[0]}''')
    st.markdown(f'''{patient_detailspd.ADDRESS_6.iloc[0]}''')
    st.markdown(f'''{patient_detailspd.POSTCODE.iloc[0]}''')
    st.markdown(f'''__GP Practice:__ {patient_detailspd.PRACTICE_NAME.iloc[0]}''')
    st.markdown(f'''__Distance from Practice in Metres:__ {round(patient_detailspd.DISTANCE_FROM_PRACTICE.iloc[0])}''')
    st.markdown(f'''__Household:__ {patient_detailspd.HOUSEHOLD_TYPE.iloc[0]}''')

st.divider()

st.markdown('#### Morbidities')

st.markdown(f''' __Diabetes:__ {patient_detailspd.DIABETES.iloc[0]}''')
st.markdown(f''' __COPD:__ {patient_detailspd.COPD.iloc[0]}''')
st.markdown(f''' __Asthma:__ {patient_detailspd.ASTHMA.iloc[0]}''')
st.markdown(f''' __Hypertension:__ {patient_detailspd.HYPERTENSION.iloc[0]}''')
st.markdown(f''' __Cancer:__ {patient_detailspd.CANCER.iloc[0]}''')
st.divider()

st.markdown('#### Medication')
st.divider()

medication = session.table('HEALTH_DB.PROCESSED_DOCUMENTS.GENERATED_MEDICATION')
medication = medication.filter(F.col('NHS_NUMBER')==patient_id)
medication = medication.select(F.col('EVENTS')['MEDICATION'].alias('MEDICATION'))
medication = medication.join_table_function('flatten',F.col('MEDICATION'))
medication = medication.select(F.col('VALUE')['MEDICATION_BNF_CODE'].astype(T.StringType()).alias('BNF_CODE'),
                              F.col('VALUE')['BNF_DESCRIPTION'].astype(T.StringType()).alias('BNF_DESCRIPTION'),
                               F.col('VALUE')['DOSAGE'].astype(T.StringType()).alias('DOSAGE'),
                               F.col('VALUE')['POSSIBLE_SIDE_EFFECTS'].astype(T.StringType()).alias('POSSIBLE_SIDE_EFFECTS')
                              )



st.write(medication)

medical_history = session.table('HEALTH_DB.PROCESSED_DOCUMENTS."Medical History"').filter(F.col('NHS_NUMBER')==patient_id).order_by(F.col('DATE').desc(),F.col('TIME').desc())

previous_gp_data = session.table('HEALTH_DB.PROCESSED_DOCUMENTS.V_HISTORIC_GP_NOTES').drop('DOC_META')

st.markdown('''#### Most recent appointment''')

st.write(medical_history.to_pandas().COMMENT.iloc[0])
st.markdown('#### Medical History')


st.table(medical_history.drop('FULL_DOCUMENT','NAME','NHS_NUMBER','APPOINTMENT_ID'))

st.markdown('#### Medical History - Paper Based System')


filtered_gp = previous_gp_data.filter(F.replace(F.col('"NHS Number"'),F.lit(' '),F.lit(''))==patient_id)

filtered_gp_pd = filtered_gp.to_pandas()

for A in filtered_gp_pd.index:

    appt_date = filtered_gp_pd['Appointment Date'].iloc[A]
    
    st.table(filtered_gp.filter(F.col('"Appointment Date"')==appt_date).drop('"NHS Number"','"Patient Name"','RELATIVE_PATH'))
    
    
    col1,col2,col3 =st.columns(([0.2,0.5,0.2]))
    with col2:
        st.image(filtered_gp.filter(F.col('"Appointment Date"')==appt_date).select(F.call_function('GET_PRESIGNED_URL',
                                                                                               '@HEALTH_DB.PROCESSED_DOCUMENTS.GP_HISTORIC_NOTES',
                                                                                               F.col('RELATIVE_PATH'))).collect()[0][0])
OBJECT_H = filtered_gp.select(F.object_construct(F.lit('NHS_NUMBER'),
                                                F.col('"NHS Number"'),
                                                F.lit('DATE'),
                                                F.col('"Appointment Date"'),
                                                F.lit('CONSULTANT'),
                                                F.col('"Consultant"'),
                                                F.lit('COMMENT'),
                                                F.col('"Notes"')).alias('MEDICAL_HISTORY'))

OBJECT_H = OBJECT_H.select(F.array_agg('MEDICAL_HISTORY').alias('HIST'))



GEN_EVENTS = session.table('HEALTH_DB.PROCESSED_DOCUMENTS.GENERATED_EVENTS').drop('ANSWER')

GEN_EVENTS = GEN_EVENTS.join(patient_details,GEN_EVENTS['NHS_NUMBER']==patient_details['NHS_NUMBER'],lsuffix='e').drop('NHS_NUMBERE')



with st.form('GenerateReport'):

    consultant = st.text_input('Name of Consultant','''Dr B O'Connor ''')

    model = st.selectbox('select model:',['snowflake-arctic','reka-core','reka-flash','mistral-large','mixtral-8x7b','llama2-70b-chat','llama3-8b','llama3-70b','mistral-7b','gemma-7b'])
    
    gen_report = st.form_submit_button('Generate Medical Report for Patient')


if gen_report:
    info = '''Create a medical synthetic followup letter based on the following fictious information:'''

    st.info(info)

    OBJECT = GEN_EVENTS.select(F.object_construct(F.lit('NHS_NUMBER'),
                                             F.col('NHS_NUMBER'),
                                            F.lit('CONSULTANT'),
                                            F.lit(consultant),
                                              F.lit('FIRST_NAME'),
                                              F.col('FIRST_NAME'),
                                              F.lit('LAST_NAME'),
                                              F.col('LAST_NAME'),
                                              F.lit('DATE_OF_BIRTH'),
                                              F.col('DATE_OF_BIRTH'),
                                              F.lit('PRACTICE_NAME'),
                                              F.col('PRACTICE_NAME'),
                                              F.lit('OCCUPATION'),
                                              F.col('OCCUPATION'),
                                              F.lit('SEX'),
                                              F.col('SEX'),
                                              F.lit('ADDRESS_1'),
                                              F.col('ADDRESS_1'),
                                              F.lit('ADDRESS_2'),
                                              F.col('ADDRESS_2'),
                                              F.lit('ADDRESS_3'),
                                              F.col('ADDRESS_3'),
                                              F.lit('ADDRESS_4'),
                                              F.col('ADDRESS_4'),
                                              F.lit('ADDRESS_5'),
                                              F.col('ADDRESS_5'),
                                              F.lit('ADDRESS_6'),
                                              F.col('ADDRESS_6'),
                                              F.lit('POSTCODE'),
                                              F.col('POSTCODE'),
                                              F.lit('MEDICAL_HISTORY'),
                                              F.col('EVENTS')
                                             
                                             
                                             ).alias('DATA'))

    OBJECT = OBJECT.join(OBJECT_H)

    hist = OBJECT_H.collect()[0][0]
    st.code(hist)

    
    st.code(OBJECT.select('DATA').collect()[0][0])

    create_letter = OBJECT.select(F.call_function('SNOWFLAKE.CORTEX.COMPLETE',model,
                                              F.concat(F.lit(info),
                                                       F.cast('DATA',T.StringType()),
                                                       F.lit('and also this historic data'),
                                                       F.cast('HIST',T.StringType()))).alias('LETTER'),
                                 F.lit('Use all details from the provided data.  Do not include any placeholders for text.'))

    st.write(create_letter.select('LETTER').to_pandas().LETTER.iloc[0])
