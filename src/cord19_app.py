import streamlit as st
import pandas as pd
import json
from utils import get_most_similar_title
from data_io import DataIO
import time
import os
import configparser

def get_result(query, df, top_n):
    return get_most_similar_title(query, df, top_n)

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_data():
    dataio=DataIO()
    df = dataio.get_data()
    return df

@st.cache()
def get_data_dir():
    config = configparser.ConfigParser()
    config.read("config.cfg")
    return config.get("DATA", "DATA_DIR")

def update_data():
    dataio=DataIO(autoload=False)
    df = dataio.update()
    if df.empty:
        st.sidebar.error("Failed To Update!")
    else:
        st.sidebar.balloons()
        st.sidebar.success("Updated Data, Wrote to disk and Loaded!")
    return df

def main():
    st.sidebar.markdown("### Updating Data takes more than 3 minutes and overwrite disk data. This is intended to be run in interval of few days!")
    if not os.path.exists(f"{get_data_dir()}/processed_metadata.pickle"):
        st.error("Using Sample Data, Use Update Data to get full results!")
    
    if st.sidebar.button("Update Data"):
        t = time.time()
        df = update_data()
        st.info(f"Time Taken: {round(time.time()-t, 5)} sec")
      
    st.title("COVID-19 Open Research Dataset Search")
    st.header("Please Enter Query/Title to Search for Similar Research Titles")
    query = st.text_input("Plain Text Only")
    top_n = st.slider('Show Top n Predicted docs?', min_value=5, max_value=30, value=5)
    st.header("Prediction")
    if st.button("Run"):
        if not query:
            st.error("Query Empty")
        else:
            with st.spinner("Running Query"):
                res = get_result(query, get_data(), top_n)
                qu = res["query"]
                p_qu = res["processed_query"]
                pred = res["pred"]
            st.markdown(f"**Query:** `{qu}`")
            st.markdown(f"**Processed Query:** `{p_qu}`")
            for k, v in pred.items():
                st.subheader(f"Rank: {k}")
                st.write(f'''<a target="_blank" href='{v["url"]}'>Open Source</a>''', unsafe_allow_html=True)
                st.json(json.dumps(v))

if __name__=="__main__":
    main()
