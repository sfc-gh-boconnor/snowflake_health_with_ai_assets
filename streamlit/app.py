import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Set page title and configuration
st.set_page_config(
    page_title="Example Streamlit App",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a title and description
st.title("Example Streamlit App")
st.markdown("""
This is a simple example Streamlit application that demonstrates some basic features.
It connects to Snowflake and visualizes data from the example table created in the notebook.
""")

# Sidebar
st.sidebar.header("Controls")
sample_size = st.sidebar.slider("Sample Size", 1, 100, 10)
chart_type = st.sidebar.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"])

# Create some sample data (in a real app, this would come from Snowflake)
def generate_sample_data(size):
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=size)
    data = {
        "date": dates,
        "value": np.random.normal(100, 15, size=size).cumsum(),
        "category": np.random.choice(["A", "B", "C"], size=size)
    }
    return pd.DataFrame(data)

# Generate data
df = generate_sample_data(sample_size)

# Display the data
st.subheader("Sample Data")
st.dataframe(df)

# Create visualization based on selected chart type
st.subheader("Visualization")

if chart_type == "Bar Chart":
    chart = alt.Chart(df).mark_bar().encode(
        x='date:T',
        y='value:Q',
        color='category:N',
        tooltip=['date', 'value', 'category']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
    
elif chart_type == "Line Chart":
    chart = alt.Chart(df).mark_line().encode(
        x='date:T',
        y='value:Q',
        color='category:N',
        tooltip=['date', 'value', 'category']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
    
else:  # Scatter Plot
    chart = alt.Chart(df).mark_circle().encode(
        x='date:T',
        y='value:Q',
        color='category:N',
        size=alt.Size('value', scale=alt.Scale(range=[50, 200])),
        tooltip=['date', 'value', 'category']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

# Add a section for Snowflake connection (just UI, not functional in this example)
st.subheader("Snowflake Connection")
with st.expander("Configure Snowflake Connection"):
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Account", placeholder="your-account.snowflakecomputing.com")
        st.text_input("Username", placeholder="username")
        st.text_input("Password", type="password")
    with col2:
        st.text_input("Warehouse", placeholder="COMPUTE_WH")
        st.text_input("Database", placeholder="DEMO_DB")
        st.text_input("Schema", placeholder="PUBLIC")
    
    st.button("Connect to Snowflake")

# Footer
st.markdown("---")
st.markdown("Created for DataOps Live Event")