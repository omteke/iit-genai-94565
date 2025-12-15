import pandas as pd
import streamlit as st
from pandasql import sqldf 

filepath = "emp_hdr.csv"
df = pd.read_csv(filepath)
st.title("Employee Data SQL Explorer")

st.subheader("Dataframe Column Types:")
st.write(df.dtypes)

st.subheader("\nEmp Data:")
st.dataframe(df)
# query = "SELECT * FROM data WHERE sal BETWEEN 1000 AND 2000 ORDER BY sal"

query = st.text_input(
    "Enter SQL Query:",
    placeholder="Enter your query here.."
)
#query = "SELECT job, SUM(sal) total FROM data GROUP BY job"
if query:
    try:
        result = sqldf(query, {"data": df})
        st.subheader("\nQuery Result:")
        st.dataframe(result)
    except Exception as e:
        st.error(f" SQL Error: {e}")
