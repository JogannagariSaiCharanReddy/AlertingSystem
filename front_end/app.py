import streamlit as st
from views import (
    user_view, 
    admin_view, 
    admin_management_view, 
    admin_analytics_view
)
import base64

st.set_page_config(
    page_title="Alerting Platform",
    layout="wide"
)

# A simple dictionary to map page names to their render functions
PAGES = {
    "👤 End User Dashboard": user_view.show_end_user_view,
    "🚨 Admin: Alert Management": admin_view.show,
    "👥 Admin: User & Team Management": admin_management_view.show,
    "📊 Admin: Analytics": admin_analytics_view.show,
}

def load_css(file_name):
    """Function to load and inject a local CSS file."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # Load custom CSS
    load_css("style.css")

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    # Get the function from the dictionary and call it
    page_function = PAGES[selection]
    page_function()

if __name__ == "__main__":
    main()