import streamlit as st
import pandas as pd
from services import backend_service

def show():
    st.title("👥 User & Team Management")

    tab1, tab2 = st.tabs(["Users", "Teams"])

    with tab1:
        st.header("Create New User")
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            teams = backend_service.list_teams()
            team_map = {team['name']: team['id'] for team in teams}

            with st.form("create_user_form"):
                email = st.text_input("Email")
                full_name = st.text_input("Full Name")
                team_name = st.selectbox("Assign to Team", options=team_map.keys(), index=None)
                
                submitted = st.form_submit_button("Create User")
                if submitted:
                    if email and full_name:
                        user_data = {
                            "email": email, "full_name": full_name,
                            "team_id": team_map.get(team_name)
                        }
                        if backend_service.create_user(user_data):
                            st.success(f"User '{full_name}' created.")
                    else:
                        st.warning("Email and Full Name are required.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.header("Existing Users")
        users = backend_service.list_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
        else:
            st.info("No users found.")

    with tab2:
        st.header("Create New Team")
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            with st.form("create_team_form"):
                name = st.text_input("Team Name")
                submitted = st.form_submit_button("Create Team")
                if submitted and name:
                    if backend_service.create_team({"name": name}):
                        st.success(f"Team '{name}' created successfully.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.header("Existing Teams")
        teams_list = backend_service.list_teams()
        if teams_list:
            st.dataframe(pd.DataFrame(teams_list), use_container_width=True)
        else:
            st.info("No teams found.")