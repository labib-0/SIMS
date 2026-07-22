import requests
import streamlit as st

@st.cache_data
def load_lottieurl(url: str):
    """
    Fetches a Lottie animation JSON from a given URL.
    Returns the JSON object if successful, else None.
    """
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        return None
