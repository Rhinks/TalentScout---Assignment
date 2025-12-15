#Streamlit application: Handles rendering, user input, and manages state - in memory database

import streamlit as st
import pandas as pd

st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4,5],
    'second column': [10, 20, 30, 40,23]
}))
