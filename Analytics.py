import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

def run():
    # 1. Page Setup
    #st.set_page_config(
       # page_title="🏡 Smart Real Estate Dashboard",
      #  layout="wide"
    #)

    # 2. Title & Intro
    st.title("🏡 Smart Real Estate Analytics")
    st.markdown("Explore real estate market trends with interactive visuals and insights.")

    # 3. Load Data
    @st.cache_data
    def load_data():
        df = pd.read_csv("data_viz1.csv")
        with open("feature_text.pkl", "rb") as f:
            feature_text = pickle.load(f)
        return df, feature_text

    df, feature_text = load_data()

    # Sidebar Filters
    st.sidebar.header("🔎 Filters")
    property_types = df['property_type'].dropna().unique().tolist()
    selected_property = st.sidebar.selectbox("Select Property Type", property_types)

    bhk_options = sorted(df['bedRoom'].dropna().unique())
    selected_bhk = st.sidebar.multiselect("Select BHK", bhk_options, default=bhk_options)

    sector_options = ['Overall'] + sorted(df['sector'].dropna().unique())
    selected_sector = st.sidebar.selectbox("Select Sector", sector_options)

    filtered_df = df[
        (df['property_type'] == selected_property) &
        (df['bedRoom'].isin(selected_bhk))
    ]
    if selected_sector != 'Overall':
        filtered_df = filtered_df[filtered_df['sector'] == selected_sector]

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Listings", len(filtered_df))
    col2.metric("Avg Price (₹ Cr)", f"{filtered_df['price'].mean():,.2f}")
    col3.metric("Avg Area (sqft)", f"{filtered_df['built_up_area'].mean():,.2f}")

    # Tabs for Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Geo & WordCloud",
        "📈 Price Analysis",
        "📊 BHK Comparison",
        "📉 Distributions",
        "🛋️ Furnishing and Age Analysis"
    ])

    # Tab 1: Geo & WordCloud
    with tab1:
        st.subheader("📍 Sector Price per Sqft Geomap")
        group_df = filtered_df.groupby('sector')[['price_per_sqft', 'built_up_area', 'latitude', 'longitude']].mean()
        fig_map = px.scatter_mapbox(
            group_df,
            lat="latitude",
            lon="longitude",
            color="price_per_sqft",
            size="built_up_area",
            zoom=10,
            mapbox_style="carto-positron",
            color_continuous_scale="Turbo",
            hover_name=group_df.index
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.subheader("🔤 Feature WordCloud")
        if isinstance(feature_text, list):
            feature_text = " ".join(str(item) for item in feature_text)
        wordcloud = WordCloud(width=800, height=600, background_color='white', colormap='plasma').generate(feature_text)
        fig_wc, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig_wc)

    # Tab 2: Area vs Price
    with tab2:
        st.subheader("📈 Area vs Price Analysis")
        df1 = pd.read_csv('gurgaon_properties_missing_value_imputation (1).csv')

        filtered_df1 = df1[
            (df1['built_up_area'] < 10000) &
            (df1['property_type'] == selected_property) &
            (df1['bedRoom'].isin(selected_bhk))
        ]
        if selected_sector != 'Overall':
            filtered_df1 = filtered_df1[filtered_df1['sector'] == selected_sector]

        furnishing_map = {0: 'Unfurnished', 1: 'Semi-Furnished', 2: 'Furnished'}
        filtered_df1['Furnishing Type'] = filtered_df1['furnishing_type'].map(furnishing_map)

        st.markdown("#### 🔹 Price vs Area (Colored by Furnishing Type, Sized by Price)")
        fig_furnish = px.scatter(
            filtered_df1,
            x="built_up_area",
            y="price",
            color="Furnishing Type",
            size="price",
            size_max=25,
            labels={"built_up_area": "Area (sq.ft)", "price": "Price (Cr ₹)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_furnish.update_traces(marker=dict(line=dict(width=0.5, color='black')), opacity=0.8)
        fig_furnish.update_layout(title="Area vs Price with Furnishing Type", title_x=0.5)
        st.plotly_chart(fig_furnish, use_container_width=True)

        st.divider()

        st.markdown("#### 🔹 Area vs Price (BHK-wise Color)")
        fig_price = px.scatter(
            filtered_df1,
            x="built_up_area",
            y="price",
            color="bedRoom",
            trendline="ols",
            color_continuous_scale="Tealrose",
            labels={"built_up_area": "Built-up Area (sq.ft)", "price": "Price (Cr ₹)", "bedRoom": "BHK"}
        )
        st.plotly_chart(fig_price, use_container_width=True)

    # Tab 3: BHK Comparison
    with tab3:
        st.subheader("🍰 BHK Distribution")
        fig_pie = px.pie(
            filtered_df,
            names='bedRoom',
            title="Distribution of BHKs",
            color_discrete_sequence=px.colors.sequential.Rainbow
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("📦 BHK vs Price Boxplot")
        box_df = filtered_df[filtered_df['bedRoom'] <= 5]
        fig_box = px.box(
            box_df,
            x='bedRoom',
            y='price',
            color='bedRoom',
            color_discrete_sequence=px.colors.qualitative.Set3,
            title="BHK-wise Price Distribution"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # Tab 4: Distribution & Correlation
    with tab4:
        st.subheader("🏷️ Price Distribution by Property Type")
        fig_dist, ax = plt.subplots(figsize=(10, 4))
        for p_type in filtered_df1['property_type'].unique():
            sns.kdeplot(
                filtered_df1[filtered_df1['property_type'] == p_type]['price'],
                label=p_type,
                ax=ax,
                linewidth=2
            )
        ax.legend()
        ax.set_facecolor('#f0f0f0')
        st.pyplot(fig_dist)

        st.subheader("🚿 Bathroom Distribution")
        fig_bath = px.pie(
            filtered_df1,
            names='bathroom',
            title='Number of Bathrooms',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_bath)

        st.subheader("🌅 Balcony Distribution")
        fig_balcony = px.pie(
            filtered_df1,
            names='balcony',
            title='Number of Balconies',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_balcony)

        st.subheader("📊 Feature Distributions")
        important_features = ['price_per_sqft', 'bathroom', 'balcony', 'built_up_area', 'luxury_score', 'price']
        for feature in important_features:
            if pd.api.types.is_numeric_dtype(filtered_df1[feature]):
                st.markdown(f"### Distribution of `{feature}`")
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.histplot(filtered_df1[feature].dropna(), kde=True, ax=ax, color='teal', bins=30)
                ax.set_xlabel(feature)
                ax.set_ylabel("Frequency")
                st.pyplot(fig)
            else:
                st.markdown(f"📝 Skipping `{feature}` (non-numeric)")

    # Tab 5: Furnishing and Age Analysis
    with tab5:
        st.subheader("🛋️ Price by Furnishing Type (Mean & Median)")

        furnish_df = filtered_df[['furnishing_type', 'price']].dropna()
        furnish_df['Furnishing Type'] = furnish_df['furnishing_type'].map(furnishing_map)

        mean_prices = furnish_df.groupby('Furnishing Type')['price'].mean().reset_index(name='Mean Price')
        median_prices = furnish_df.groupby('Furnishing Type')['price'].median().reset_index(name='Median Price')

        price_summary = pd.merge(mean_prices, median_prices, on='Furnishing Type')
        price_melted = price_summary.melt(id_vars='Furnishing Type', var_name='Statistic', value_name='Price')

        fig_grouped = px.bar(
            price_melted,
            x='Furnishing Type',
            y='Price',
            color='Statistic',
            barmode='group',
            title='🏡 Mean vs Median Price by Furnishing Type',
            text='Price',
            color_discrete_map={
                'Mean Price': '#1f77b4',
                'Median Price': '#ff7f0e'
            }
        )
        fig_grouped.update_traces(texttemplate='₹%{text:.2f}', textposition='outside')
        fig_grouped.update_layout(
            xaxis_title="Furnishing Type",
            yaxis_title="Price (₹ Cr)",
            plot_bgcolor='#f9f9f9',
            legend_title="Statistic",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )
        st.plotly_chart(fig_grouped, use_container_width=True)

        st.subheader("🏗️ Price by Age of Property (Mean & Median)")
        age_df = filtered_df[['agePossession', 'price']].dropna()

        mean_price_age = age_df.groupby('agePossession')['price'].mean().reset_index(name='Mean Price')
        median_price_age = age_df.groupby('agePossession')['price'].median().reset_index(name='Median Price')

        age_price_summary = pd.merge(mean_price_age, median_price_age, on='agePossession')
        age_price_melted = age_price_summary.melt(id_vars='agePossession', var_name='Statistic', value_name='Price')

        fig_age = px.bar(
            age_price_melted,
            x='agePossession',
            y='Price',
            color='Statistic',
            barmode='group',
            title='🏗️ Mean vs Median Price by Age of Property',
            text='Price',
            color_discrete_map={
                'Mean Price': '#2ca02c',
                'Median Price': '#d62728'
            }
        )
        fig_age.update_traces(texttemplate='₹%{text:.2f}', textposition='outside')
        fig_age.update_layout(
            xaxis_title="Age of Property",
            yaxis_title="Price (₹ Cr)",
            plot_bgcolor='#f9f9f9',
            legend_title="Statistic",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )
        st.plotly_chart(fig_age, use_container_width=True)

# To run the app
if __name__ == "__main__":
    run()
