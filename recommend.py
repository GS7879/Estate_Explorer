import streamlit as st
import pandas as pd
import numpy as np
import pickle

def run():
    # ── Load data ─────────────────────────────────────────────
    location_df = pickle.load(open('location_df.pkl', 'rb'))
    cosine_sim1  = pickle.load(open('cosine_sim1.pkl', 'rb'))
    cosine_sim2  = pickle.load(open('cosine_sim2.pkl', 'rb'))
    cosine_sim3  = pickle.load(open('cosine_sim3.pkl', 'rb'))

    # Main apartment dataset
    df = pd.read_csv('appartments (1).csv')
    df.set_index('PropertyName', inplace=True)

    # ── Streamlit setup ───────────────────────────────────────
   # st.set_page_config(
      #  page_title="🏠 Property Recommendation System",
       # page_icon="🏡",
       # layout="centered"
   # )
    st.title("🏡 Smart Property Recommendation System")

    # ── Recommendation helper ────────────────────────────────
    def recommend_properties_with_scores(property_name, top_n=5):
        cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + 1 * cosine_sim3
        sim_scores = list(
            enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)])
        )
        sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        top_indices   = [i[0] for i in sorted_scores[1 : top_n + 1]]
        top_scores    = [i[1] for i in sorted_scores[1 : top_n + 1]]
        top_properties = location_df.index[top_indices].tolist()
        links = df.loc[top_properties, 'Link'].tolist()

        recommendations_df = pd.DataFrame({
            '🏢 Property Name' : top_properties,
            '📊 Similarity Score' : [round(score, 3) for score in top_scores],
            '🔗 Link' : links
        })
        recommendations_df['🔗 Link'] = recommendations_df['🔗 Link'].apply(
            lambda url: f"[Visit Property]({url})" if pd.notna(url) else "No Link"
        )
        return recommendations_df

    # ── Location‑based search ─────────────────────────────────
    st.header("📍 Search Properties by Location")
    selected_location = st.selectbox(
        'Choose a Landmark or Location:',
        sorted(location_df.columns.to_list())
    )
    radius = st.number_input(
        'Enter Radius (in km):',
        min_value=0.0,
        step=0.5
    )

    if st.button('🔍 Find Properties Nearby'):
        result_ser = location_df[
            location_df[selected_location] < radius * 1000
        ][selected_location].sort_values()

        if result_ser.empty:
            st.warning("No properties found within the given radius.")
        else:
            st.success(f"Properties within {radius} km of {selected_location}:")
            for key, value in result_ser.items():
                st.markdown(f"✔️ **{key}** – {round(value / 1000, 2)} km")

    # ── Similar property recommendations ─────────────────────
    st.header("🏙️ Recommend Similar Properties")
    selected_appartment = st.selectbox(
        'Select a Property to Get Recommendations:',
        sorted(location_df.index.to_list())
    )

    if st.button('✨ Recommend Similar Properties'):
        recommendation_df = recommend_properties_with_scores(selected_appartment)
        st.markdown(
            f"🎯 Showing top {len(recommendation_df)} recommendations "
            f"similar to **{selected_appartment}**:"
        )
        st.write(recommendation_df.to_markdown(index=False), unsafe_allow_html=True)

# ── Run the app when executed directly ───────────────────────
if __name__ == "__main__":
    run()

