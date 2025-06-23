import streamlit as st
import pandas as pd
import numpy as np
import pickle
import gdown
import os

def run():
    # Styling
    st.markdown(
        """
        <style>
            .stApp { background-color: #e3f2fd; }
            .css-18e3th9 {
                background-color: #fffaf0;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
            }
            h1 { color: #00796b; }
            .stSelectbox > div, .stNumberInput > div {
                border-radius: 8px !important;
            }
            .stButton > button {
                background-color: #00796b;
                color: white;
                border-radius: 8px;
                padding: 0.5rem 1rem;
            }
            .stButton > button:hover {
                background-color: #004d40;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Load df.pkl (local required)
    with open('df.pkl', 'rb') as file:
        df = pickle.load(file)

    # ⚡️ DOWNLOAD pipeline.pkl from GDrive if not already present
    pipeline_file = "pipeline.pkl"
    if not os.path.exists(pipeline_file):
        st.warning("Downloading pipeline model from Google Drive...")
        gdown.download(
            "https://drive.google.com/uc?export=download&id=1MMfsoyN6JTKt_ICPOPWs8-EUPaUmtGGF",
            pipeline_file,
            quiet=False
        )

    # Load the pipeline
    with open(pipeline_file, "rb") as file:
        pipeline = pickle.load(file)

    # App title and description
    st.markdown("<h1>🏡 Real Estate Price Predictor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555;'>Enter property details below to estimate your price range with confidence and clarity.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        property_type = st.selectbox('🏘️ Property Type', ['flat', 'house'])
        sector = st.selectbox('📍 Sector', sorted(df['sector'].unique()))
        bedrooms = float(st.selectbox('🛏️ Number of Bedrooms', sorted(df['bedRoom'].unique())))
        bathroom = float(st.selectbox('🛁 Number of Bathrooms', sorted(df['bathroom'].unique())))
        balcony = st.selectbox('🌇 Number of Balconies', sorted(df['balcony'].unique()))
        property_age = st.selectbox('📅 Property Age', sorted(df['agePossession'].unique()))

    with col2:
        built_up_area = float(st.number_input('📐 Built-Up Area (in sq.ft)', value=0.0))
        servant_room = float(st.selectbox('🧹 Servant Room', [0.0, 1.0]))
        store_room = float(st.selectbox('📦 Store Room', [0.0, 1.0]))
        furnishing_type = st.selectbox('🛋️ Furnishing Type', sorted(df['furnishing_type'].unique()))
        luxury_category = st.selectbox('💎 Luxury Category', sorted(df['luxury_category'].unique()))
        floor_category = st.selectbox('🏢 Floor Category', sorted(df['floor_category'].unique()))

    if st.button('🔍 Predict Price'):
        with st.spinner('Calculating price range...'):
            data = [[property_type, sector, bedrooms, bathroom, balcony, property_age,
                     built_up_area, servant_room, store_room, furnishing_type,
                     luxury_category, floor_category]]

            columns = ['property_type', 'sector', 'bedRoom', 'bathroom', 'balcony',
                       'agePossession', 'built_up_area', 'servant room', 'store room',
                       'furnishing_type', 'luxury_category', 'floor_category']

            one_df = pd.DataFrame(data, columns=columns)

            base_price = np.expm1(pipeline.predict(one_df))[0]
            low = base_price - 0.22
            high = base_price + 0.22

            st.success(f"💰 **Estimated Price Range:** ₹ {round(low, 2)} Cr — ₹ {round(high, 2)} Cr")


# 🔁 This prevents code from auto-executing when imported
if __name__ == "__main__":
    run()
