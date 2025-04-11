import streamlit as st
import pandas as pd
import numpy as np
import datetime
import data_processor
import alert_system
import visualization

# Set page configuration
st.set_page_config(
    page_title="Elderly Care Monitoring System",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'health_data' not in st.session_state:
    st.session_state.health_data = None
if 'safety_data' not in st.session_state:
    st.session_state.safety_data = None
if 'reminder_data' not in st.session_state:
    st.session_state.reminder_data = None
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Load data
def load_data():
    try:
        import database
        
        # Setup database if not already set up
        database.setup_database()
        
        # Get data from database
        health_data = database.get_health_data()
        safety_data = database.get_safety_data()
        reminder_data = database.get_reminder_data()
        
        # Process data
        st.session_state.health_data = data_processor.process_health_data(health_data)
        st.session_state.safety_data = data_processor.process_safety_data(safety_data)
        st.session_state.reminder_data = data_processor.process_reminder_data(reminder_data)
        
        # Generate alerts
        st.session_state.alerts = alert_system.generate_alerts(
            st.session_state.health_data,
            st.session_state.safety_data,
            st.session_state.reminder_data
        )
        
        # Save alerts to database
        for alert in st.session_state.alerts:
            database.save_alert(
                device_id=alert['Device-ID'],
                alert_type=alert['Alert Type'],
                timestamp=alert['Timestamp'],
                status=alert['Status'],
                message=alert['Message'],
                priority=alert['Priority']
            )
        
        st.session_state.last_update = datetime.datetime.now()
        return True
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return False

# Main dashboard
def main_dashboard():
    # Header
    st.title("Elderly Care Multi-Agent Monitoring System")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Dashboard Controls")
        if st.button("Refresh Data"):
            with st.spinner("Loading data..."):
                success = load_data()
                if success:
                    st.success("Data refreshed successfully!")
        
        st.subheader("Filter by User/Device")
        if st.session_state.health_data is not None:
            device_options = ['All'] + sorted(st.session_state.health_data['Device-ID/User-ID'].unique().tolist())
            selected_device = st.selectbox("Select Device/User", device_options)
            
            if selected_device != 'All':
                # Filter data for selected device
                st.session_state.filtered_health = st.session_state.health_data[
                    st.session_state.health_data['Device-ID/User-ID'] == selected_device
                ]
                st.session_state.filtered_safety = st.session_state.safety_data[
                    st.session_state.safety_data['Device-ID/User-ID'] == selected_device
                ]
                st.session_state.filtered_reminder = st.session_state.reminder_data[
                    st.session_state.reminder_data['Device-ID/User-ID'] == selected_device
                ]
            else:
                st.session_state.filtered_health = st.session_state.health_data
                st.session_state.filtered_safety = st.session_state.safety_data
                st.session_state.filtered_reminder = st.session_state.reminder_data
        
        st.write("Last updated:", st.session_state.last_update)
    
    # Check if data is loaded
    if st.session_state.health_data is None:
        st.info("Please load data using the 'Refresh Data' button in the sidebar.")
        return
    
    # Alert section
    st.header("🚨 Active Alerts")
    if st.session_state.alerts:
        alerts_df = pd.DataFrame(st.session_state.alerts)
        alerts_to_show = alerts_df if 'filtered_health' not in st.session_state else \
            alerts_df[alerts_df['Device-ID'].isin(st.session_state.filtered_health['Device-ID/User-ID'].unique())]
        
        if len(alerts_to_show) > 0:
            st.dataframe(alerts_to_show[['Device-ID', 'Alert Type', 'Timestamp', 'Status', 'Message']], 
                        use_container_width=True,
                        height=200)
            
            # Action buttons for selected alert
            col1, col2 = st.columns(2)
            with col1:
                selected_alert_idx = st.selectbox("Select Alert to Respond:", 
                                                range(len(alerts_to_show)),
                                                format_func=lambda i: f"{alerts_to_show.iloc[i]['Device-ID']} - {alerts_to_show.iloc[i]['Alert Type']}")
            with col2:
                if st.button("Mark as Resolved"):
                    # Get the selected alert
                    selected_alert = alerts_to_show.iloc[selected_alert_idx]
                    # Update status in database
                    import database
                    alert_id = selected_alert.get('id', selected_alert_idx + 1)  # Fallback to index+1 if id not present
                    success = database.update_alert_status(alert_id, "Resolved")
                    # Update local alerts data
                    st.session_state.alerts[selected_alert_idx]['Status'] = "Resolved"
                    
                    if success:
                        # Notify caregiver
                        alert_system.notify_caregiver(st.session_state.alerts[selected_alert_idx])
                        st.success("Alert marked as resolved and caregiver notified!")
                    else:
                        st.error("Failed to update alert status in database.")
        else:
            st.success("No active alerts for the selected device.")
    else:
        st.success("No active alerts at this time.")
    
    # Dashboard overview
    st.header("Dashboard Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Health Metrics")
        health_stats = data_processor.get_health_stats(st.session_state.filtered_health)
        st.metric("Abnormal Heart Rate", f"{health_stats['abnormal_hr']}%")
        st.metric("Abnormal Blood Pressure", f"{health_stats['abnormal_bp']}%")
        st.metric("Abnormal Glucose", f"{health_stats['abnormal_glucose']}%")
        st.metric("Low SpO₂", f"{health_stats['low_spo2']}%")
        if st.button("View Health Details", key="health_btn"):
            st.switch_page("pages/health_monitoring.py")
    
    with col2:
        st.subheader("Safety Monitoring")
        safety_stats = data_processor.get_safety_stats(st.session_state.filtered_safety)
        st.metric("Fall Incidents", safety_stats['fall_count'])
        st.metric("High Impact Falls", safety_stats['high_impact_falls'])
        st.metric("Avg. Inactivity Duration", f"{safety_stats['avg_inactivity_duration']:.1f} sec")
        st.metric("Alerts Triggered", safety_stats['alerts_triggered'])
        if st.button("View Safety Details", key="safety_btn"):
            st.switch_page("pages/safety_monitoring.py")
    
    with col3:
        st.subheader("Reminder Compliance")
        reminder_stats = data_processor.get_reminder_stats(st.session_state.filtered_reminder)
        st.metric("Medication Reminders", reminder_stats['medication_count'])
        st.metric("Appointment Reminders", reminder_stats['appointment_count'])
        st.metric("Reminder Sent Rate", f"{reminder_stats['sent_rate']:.1f}%")
        st.metric("Acknowledgment Rate", f"{reminder_stats['ack_rate']:.1f}%")
        if st.button("View Reminder Details", key="reminder_btn"):
            st.switch_page("pages/reminders.py")
    
    # Summary charts
    st.header("Summary Visualizations")
    tab1, tab2, tab3 = st.tabs(["Health Trends", "Safety Overview", "Reminder Effectiveness"])
    
    with tab1:
        health_fig = visualization.plot_health_summary(st.session_state.filtered_health)
        st.plotly_chart(health_fig, use_container_width=True)
    
    with tab2:
        safety_fig = visualization.plot_safety_summary(st.session_state.filtered_safety)
        st.plotly_chart(safety_fig, use_container_width=True)
    
    with tab3:
        reminder_fig = visualization.plot_reminder_summary(st.session_state.filtered_reminder)
        st.plotly_chart(reminder_fig, use_container_width=True)
    
    # Predictive insights
    st.header("Predictive Insights")
    if st.button("View Predictions and Risk Analysis"):
        st.switch_page("pages/predictions.py")

# Run the dashboard
if __name__ == "__main__":
    main_dashboard()
    # First load of data
    if st.session_state.health_data is None:
        with st.spinner("Loading initial data..."):
            load_data()
            st.rerun()
