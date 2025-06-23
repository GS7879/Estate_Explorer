import streamlit as st
import dashboard
import Analytics
import recommend

# ── App configuration (Must be first Streamlit command) ─────────────────────
st.set_page_config(page_title="🏠 EstateXplorer", page_icon="🏡", layout="centered")


# ── Main application launcher ───────────────────────────────────────────────
def main():
    # App headline and description
    st.title("🏠 RealtyInsight — Data-Driven Real Estate Exploration and Analytics")
    st.markdown(
        """
        Welcome to **RealtyInsight**, your smart companion for real estate discovery.  
        🔍 Explore powerful tools for analyzing market trends, predicting prices, and discovering the best properties — all in one place.

        ---
        """
    )

    # Sidebar menu
    st.sidebar.header("📂 Navigation")
    app_choice = st.sidebar.radio(
        "Choose a module to explore:",
        ["🏠Price Predictor", "📈 Smart Analysis", "🔍 Recommend Property"]
    )

    # Informative footer or call-to-action
    st.sidebar.markdown("---")
    st.sidebar.info("👨‍💼 Designed for data enthusiasts, realtors, and curious home seekers.")

    # Launch selected module
    if app_choice == "🏠Price Predictor":
        st.subheader("🏠 Price Prediction Dashboard")
        dashboard.run()

    elif app_choice == "📈 Smart Analysis":
        st.subheader("📊 Market Insights & Analytics")
        Analytics.run()

    elif app_choice == "🔍 Recommend Property":
        st.subheader("🏙️ Smart Property Recommendations")
        recommend.run()


# ── Run the app ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
