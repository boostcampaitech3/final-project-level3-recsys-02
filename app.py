import numpy as np
import pandas as pd
import requests
import streamlit as st


def draw():
    userID = 'test-user'
    longitude = 37.44354
    latitude = 127.0560482
    payload = {
        'userID': userID,
        'longitude': longitude,
        'latitude': latitude,
    }
    response = requests.post('http://localhost:8000/request', json=payload)
    data = response.json()

    if response is not None:
        df = pd.DataFrame(
            np.random.randn(data['response'][0], data['response'][1]) / [50, 50] + [longitude, latitude],
            columns=['lat', 'lon'])
        st.map(df)


st.button('mark', on_click=draw)
