import streamlit as st
import pandas as pd
from services import backend_service

def show():
    st.title("🚨 Alert Management")

    tab1, tab2 = st.tabs(["Create & View Alerts", "Update / Archive an Alert"])

    with tab1:
        st.header("Create New Alert")
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            users = backend_service.list_users()
            teams = backend_service.list_teams()
            
            if not users:
                st.error("Cannot create alerts. At least one user must exist.")
                return
                
            user_map = {f"{user['full_name']} ({user['email']})": user['id'] for user in users}
            team_map = {team['name']: team['id'] for team in teams}

            with st.form("create_alert_form"):
                title = st.text_input("Title")
                message_body = st.text_area("Message Body", height=150)
                severity = st.selectbox("Severity", ["INFO", "WARNING", "CRITICAL"])
                creator_name = st.selectbox("Created By (Admin)", options=user_map.keys())
                is_org_wide = st.checkbox("Entire Organization")
                target_team_names = st.multiselect("Target Teams", options=team_map.keys(), disabled=is_org_wide)
                target_user_names = st.multiselect("Target Users", options=user_map.keys(), disabled=is_org_wide)

                submitted = st.form_submit_button("Create Alert")
                if submitted and title and message_body:
                    alert_data = {
                        "title": title, "message_body": message_body, "severity": severity,
                        "is_org_wide": is_org_wide,
                        "target_team_ids": [team_map[name] for name in target_team_names],
                        "target_user_ids": [user_map[name] for name in target_user_names],
                        "created_by_id": user_map[creator_name]
                    }
                    if backend_service.create_alert(alert_data):
                        st.success("Alert created!")
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.header("View Alerts & Actions")

        if st.button("🔄 Trigger Reminder Cycle"):
            with st.spinner("Processing reminders..."):
                result = backend_service.trigger_reminders()
                st.success(result.get('message', 'Reminders processed.'))
        
        col1, col2 = st.columns(2)
        severity_filter = col1.selectbox("Filter by Severity", ["ALL", "INFO", "WARNING", "CRITICAL"])
        archived_filter = col2.selectbox("Filter by Status", ["Active", "Archived"])

        params = {"is_archived": archived_filter == "Archived"}
        if severity_filter != "ALL":
            params["severity"] = severity_filter

        alerts_data = backend_service.get_all_alerts_for_admin(params)
        if alerts_data:
            st.dataframe(pd.DataFrame(alerts_data), use_container_width=True)
        else:
            st.info("No alerts match the current filters.")


    with tab2:
        st.header("Modify an Existing Alert")
        all_alerts = backend_service.get_all_alerts_for_admin()
        if not all_alerts:
            st.info("No alerts exist to modify.")
            return

        alert_map = {f"ID {a['id']}: {a['title']}": a['id'] for a in all_alerts}
        selected_alert_title = st.selectbox("Select an Alert to Modify", options=alert_map.keys())

        if selected_alert_title:
            alert_id = alert_map[selected_alert_title]
            alert_details = backend_service.get_alert_by_id(alert_id)

            if alert_details:
                with st.container():
                    st.markdown('<div class="form-container">', unsafe_allow_html=True)
                    with st.form("update_alert_form"):
                        st.subheader(f"Editing Alert ID: {alert_id}")
                        title = st.text_input("Title", value=alert_details['title'])
                        message_body = st.text_area("Message", value=alert_details['message_body'], height=150)
                        
                        submitted = st.form_submit_button("Update Alert")
                        if submitted:
                            update_data = {"title": title, "message_body": message_body}
                            if backend_service.update_alert(alert_id, update_data):
                                st.success("Alert updated successfully!")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.divider()
                st.subheader("Archive Alert")
                if st.button("Archive this Alert", type="primary"):
                    if backend_service.archive_alert(alert_id):
                        st.success("Alert archived!")