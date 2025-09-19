import streamlit as st
import pandas as pd
from services import backend_service

def show_end_user_view():
    st.title("Your Active Alerts")

    # --- User selection to simulate login ---
    users = backend_service.list_users()
    if not users:
        st.error("No users found. Please create a user in the Admin panel.")
        return

    user_map = {f"{user['full_name']} ({user['email']})": user['id'] for user in users}
    selected_user_name = st.selectbox("Select User to View Alerts For:", options=user_map.keys())
    selected_user_id = user_map[selected_user_name]
    
    st.divider()

    # --- Display Alerts for the selected user ---
    user_alerts = backend_service.get_alerts_for_user(selected_user_id)

    if not user_alerts:
        st.success("🎉 No active alerts for you. All clear!")
        return

    for alert in user_alerts:
        alert_id = alert['id']
        status = alert['personal_status']['status']
        snoozed_until = alert['personal_status']['snoozed_until']
        severity = alert['severity']
        
        card_class = f"alert-card alert-card-{severity}"

        with st.container():
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            # Card content
            st.subheader(alert['title'])
            st.caption(f"Severity: {severity} | Created: {pd.to_datetime(alert['start_time']).strftime('%Y-%m-%d %H:%M')}")
            st.write(alert['message_body'])

            st.markdown("</div>", unsafe_allow_html=True)

            # Action buttons and status below the card
            col1, col2 = st.columns([1, 1])
            with col1:
                if snoozed_until and pd.to_datetime(snoozed_until) > pd.Timestamp.utcnow():
                    st.info(f"Snoozed until {pd.to_datetime(snoozed_until).strftime('%H:%M:%S')}")
                elif status == 'READ':
                    st.success("✓ Marked as Read")
                else: # UNREAD and not snoozed
                    if st.button("Mark as Read", key=f"read_{alert_id}"):
                        if backend_service.mark_as_read(selected_user_id, alert_id):
                            st.rerun()
            
            with col2:
                if not (snoozed_until and pd.to_datetime(snoozed_until) > pd.Timestamp.utcnow()):
                     if st.button("Snooze for Today", key=f"snooze_{alert_id}"):
                        if backend_service.snooze_alert(selected_user_id, alert_id):
                            st.rerun()
            st.write("") # Spacer