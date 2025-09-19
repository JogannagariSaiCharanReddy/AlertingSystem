import streamlit as st
import pandas as pd
from services import backend_service

def show():
    st.title("📊 Analytics Dashboard")

    data = backend_service.get_analytics_dashboard()

    if not data:
        st.warning("Could not retrieve analytics data.")
        return

    # --- Overall Stats ---
    st.header("Overall Statistics")
    stats = data['overall_stats']
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Alerts Created", stats['total_alerts_created'])
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Notifications Sent", stats['total_notifications_sent'])
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Reads", stats['total_reads'])
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Currently Snoozed", stats['active_snoozes'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()

    # --- Severity Breakdown & Performance ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header("Alerts by Severity")
        severity = data['severity_breakdown']
        severity_df = pd.DataFrame.from_dict(severity, orient='index', columns=['Count'])
        st.bar_chart(severity_df, color="#00ADB5")

    with col2:
        st.header("Individual Alert Performance")
        performance = data['alerts_performance']
        if performance:
            perf_df = pd.DataFrame(performance).set_index('alert_id')
            st.dataframe(perf_df, use_container_width=True)
        else:
            st.info("No alert performance data available yet.")