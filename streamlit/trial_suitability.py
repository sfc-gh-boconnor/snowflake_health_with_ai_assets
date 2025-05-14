# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F
from snowflake.snowpark import types as T
import pydeck as pdk

logo = 'snowflake_logo_color_rgb.svg'
with open('extra.css') as ab:
    st.markdown(f"<style>{ab.read()}</style>", unsafe_allow_html=True)

st.logo(logo)
# Write directly to the app

st.markdown('<h0black>COVID TRIAL | </h0black><h0blue>PANEL DETAILS</h0blue><BR>', unsafe_allow_html=True)
#st.title("🦠 COVID Trial Panel Details 🦠 ")
st.markdown(
    """<body> Individual consent plus further background information about the patient and suitability for the trial</h1sub>""",
    unsafe_allow_html=True
    
)

# Get the current credentials
session = get_active_session()

st.markdown('''<h1sub> Covid Trial Consent Form</h1sub>''',unsafe_allow_html=True)
covid = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA.COVID_VACCINE_CONSENTS')
covid = covid.drop('DOC_META')






patients = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA.GP_NOTES_CLEANED').select('NHS_NUMBER')
patients = patients.join(covid,covid['"NHS Number"']==patients['NHS_NUMBER']).select('NHS_NUMBER').distinct()
with st.sidebar:
    patient_id = st.selectbox('Choose Patient:', patients)


patient_details = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA.SYNTHETIC_POPULATION').filter(F.col('NHS_NUMBER')==patient_id).limit(1)

patient_details = patient_details.with_column('CANCER',F.when(F.col('CANCER')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('COPD',F.when(F.col('COPD')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('ASTHMA',F.when(F.col('ASTHMA')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('HYPERTENSION',F.when(F.col('HYPERTENSION')==1,F.lit('✅')).otherwise(F.lit('❌'))      )
patient_details = patient_details.with_column('DIABETES',F.when(F.col('DIABETES')==1,F.lit('✅')).otherwise(F.lit('❌'))      )



covid = covid.filter(F.col('"NHS Number"')==patient_id)


col1,col2,col3 = st.columns([0.5,0.1,0.4])
with col1:
    c_consents_pd = covid.to_pandas()
    st.write(f'''Vaccination Brand: **{c_consents_pd['Vaccination Brand'].iloc[0]}** ''')
    st.write(f'''Consent: **{c_consents_pd['CONSENT (Y/N)'].iloc[0]}** ''')
    st.write(f'''Injection Arm: **{c_consents_pd['Injection Arm'].iloc[0]}** ''')
    st.write(f'''Reason for No Vacccine: **{c_consents_pd['Reason for no vaccine'].iloc[0]}** ''')

st.divider()


#st.write(covid)


patient_detailspd = patient_details.to_pandas()


#st.write(patient_details)

st.markdown('''<h1sub> Patient Information</h1sub>''',unsafe_allow_html=True)
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

st.markdown('''<h1sub> MORBIDITIES</h1sub>''',unsafe_allow_html=True)

st.markdown(f''' __Diabetes:__ {patient_detailspd.DIABETES.iloc[0]}''')
st.markdown(f''' __COPD:__ {patient_detailspd.COPD.iloc[0]}''')
st.markdown(f''' __Asthma:__ {patient_detailspd.ASTHMA.iloc[0]}''')
st.markdown(f''' __Hypertension:__ {patient_detailspd.HYPERTENSION.iloc[0]}''')
st.markdown(f''' __Cancer:__ {patient_detailspd.CANCER.iloc[0]}''')
st.divider()

st.markdown('''<h1sub>MEDICATION</h1sub>''',unsafe_allow_html=True)
st.divider()

medication = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA.GENERATED_MEDICATION')
medication = medication.filter(F.col('NHS_NUMBER')==patient_id)
medication = medication.select(F.col('EVENTS')['MEDICATION'].alias('MEDICATION'))
medication = medication.join_table_function('flatten',F.col('MEDICATION'))
medication = medication.select(F.col('VALUE')['MEDICATION_BNF_CODE'].astype(T.StringType()).alias('BNF_CODE'),
                              F.col('VALUE')['BNF_DESCRIPTION'].astype(T.StringType()).alias('BNF_DESCRIPTION'),
                               F.col('VALUE')['DOSAGE'].astype(T.StringType()).alias('DOSAGE'),
                               F.col('VALUE')['POSSIBLE_SIDE_EFFECTS'].astype(T.StringType()).alias('POSSIBLE_SIDE_EFFECTS')
                              )



st.write(medication)

st.divider()

st.markdown('''<h1sub> LATEST ECG</h1sub>''',unsafe_allow_html=True)

diagnostics = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA.COVID_TRIAL_DIAGNOSTICS')

diagnostics = diagnostics.filter(F.col('NHS_NUMBER')==patient_id)
ecg = diagnostics.select('ECG').collect()[0][0]
lung_function = diagnostics.select('LUNG_FUNCTION').collect()[0][0]

st.write(ecg)
st.markdown('''<h1sub> LATEST LUNG FUNCTION TEST </h1sub>''',unsafe_allow_html=True)
st.write(lung_function)

medical_history = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA."Medical History"').filter(F.col('NHS_NUMBER')==patient_id).order_by(F.col('DATE').desc(),F.col('TIME').desc())

previous_gp_data = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA.GP_NOTES_CLEANED')

st.markdown('''<h1sub> MOST RECENT APPOINTMENT</h1sub>''',unsafe_allow_html=True)

st.write(medical_history.to_pandas().COMMENT.iloc[0])
st.markdown('''<h1sub> MEDICAL HISTORY </h1sub>''',unsafe_allow_html=True)


st.table(medical_history.drop('FULL_DOCUMENT','NAME','NHS_NUMBER','APPOINTMENT_ID'))

st.markdown('''<h1sub> MEDICAL HISTORY - PAPER BASED</h1sub>''',unsafe_allow_html=True)


filtered_gp = previous_gp_data.filter(F.col('NHS_NUMBER')==patient_id)

filtered_gp_pd = filtered_gp.to_pandas()

for A in filtered_gp_pd.index:

    appt_date = filtered_gp_pd['APPOINTMENT_DATE'].iloc[A]
    
    st.table(filtered_gp.filter(F.col('APPOINTMENT_DATE')==appt_date).drop('NHS_NUMBER','PATIENT_NAME','RELATIVE_PATH'))
    
    
    col1,col2,col3 =st.columns(([0.2,0.5,0.2]))
    with col2:
        st.image(filtered_gp.filter(F.col('APPOINTMENT_DATE')==appt_date)\
                 .select(F.call_function('GET_PRESIGNED_URL',
                    '@DEFAULT_DATABASE.DOCUMENT_AI.GP_NOTES',
                    F.col('RELATIVE_PATH'))).collect()[0][0])






OBJECT_H = filtered_gp.select(F.object_construct(F.lit('NHS_NUMBER'),
                                                F.col('NHS_NUMBER'),
                                                F.lit('DATE'),
                                                F.col('APPOINTMENT_DATE'),
                                                F.lit('CONSULTANT'),
                                                F.col('CONSULTANT'),
                                                F.lit('COMMENT'),
                                                F.col('GP_NOTES')).alias('MEDICAL_HISTORY'))

OBJECT_H = OBJECT_H.select(F.array_agg('MEDICAL_HISTORY').alias('HIST'))



st.divider()

st.markdown('''<h1sub>COVID TRIAL SUITABILITY</h1sub>''',unsafe_allow_html=True)

GEN_EVENTS = session.table('DEFAULT_DATABASE.DEFAULT_SCHEMA.GENERATED_EVENTS').drop('ANSWER')

GEN_EVENTS = GEN_EVENTS.join(patient_details,GEN_EVENTS['NHS_NUMBER']==patient_details['NHS_NUMBER'],lsuffix='e').drop('NHS_NUMBERE')





with st.form('GenerateReport'):

    consultant = st.text_input('Name of Consultant','''Dr B O'Connor ''')

    model = st.selectbox('select model:',['mistral-large2','mixtral-8x7b','llama3.2-1b','mistral-7b','gemma-7b','claude-3-5-sonnet'])
    
    gen_report = st.form_submit_button('Generate Covid Suitability Report for Patient')


if gen_report:

    st.info('Create a medical synthetic report summarizing the suitability of a covid vaccine trial based on the following fictious information')

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
                                              F.col('EVENTS'),
                                              F.lit('LATEST_ECG'),
                                             F.lit(ecg),
                                                F.lit('LATEST_LUNG_FUNCTION'),
                                                  F.lit(lung_function)
                                            
                                             
                                             
                                             ).alias('DATA'))

    OBJECT = OBJECT.join(OBJECT_H)

    hist = OBJECT_H.collect()[0][0]
    st.code(hist)

    
    st.code(OBJECT.select('DATA').collect()[0][0])

    create_letter = OBJECT.select(F.call_function('SNOWFLAKE.CORTEX.COMPLETE',model,
                                              F.concat(F.lit('Create a medical synthetic report to suggest the suitability of a covid vaccine trial based on the following fictious information:'),
                                                       F.cast('DATA',T.StringType()),
                                                       F.lit('and also this historic data'),
                                                       F.cast('HIST',T.StringType()))).alias('LETTER'))

    st.write(create_letter.select('LETTER').to_pandas().LETTER.iloc[0])
