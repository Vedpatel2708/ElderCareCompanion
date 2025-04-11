import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data_processor
import visualization

# Set page config
st.set_page_config(
    page_title="Reminders - Elderly Care System",
    page_icon="🔔",
    layout="wide"
)

# Initialize session state if needed
if 'reminder_data' not in st.session_state:
    st.warning("Please return to the main dashboard to load data first.")
    st.stop()

def main():
    # Header
    st.title("🔔 Reminders Management Dashboard")
    st.write("Track and manage daily reminders for medication, appointments, and activities")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # User/Device filter
        device_options = ['All'] + sorted(st.session_state.reminder_data['Device-ID/User-ID'].unique().tolist())
        selected_device = st.selectbox("Select Device/User", device_options)
        
        # Date range filter
        min_date = st.session_state.reminder_data['Timestamp'].dt.date.min()
        max_date = st.session_state.reminder_data['Timestamp'].dt.date.max()
        
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = date_range[0]
            end_date = date_range[0]
        
        # Reminder type filter
        reminder_types = st.session_state.reminder_data['Reminder Type'].unique().tolist()
        selected_types = st.multiselect(
            "Filter by Reminder Type",
            options=reminder_types,
            default=reminder_types
        )
        
        # Status filters
        status_options = [
            "All Reminders",
            "Sent Only",
            "Not Sent",
            "Acknowledged",
            "Sent but Not Acknowledged"
        ]
        selected_status = st.selectbox("Filter by Status", status_options)
        
        # Apply filters
        filtered_reminders = st.session_state.reminder_data.copy()
        
        if selected_device != 'All':
            filtered_reminders = filtered_reminders[filtered_reminders['Device-ID/User-ID'] == selected_device]
        
        filtered_reminders = filtered_reminders[
            (filtered_reminders['Timestamp'].dt.date >= start_date) & 
            (filtered_reminders['Timestamp'].dt.date <= end_date)
        ]
        
        if selected_types:
            filtered_reminders = filtered_reminders[filtered_reminders['Reminder Type'].isin(selected_types)]
        
        # Apply status filter
        if selected_status == "Sent Only":
            filtered_reminders = filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True]
        elif selected_status == "Not Sent":
            filtered_reminders = filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == False]
        elif selected_status == "Acknowledged":
            filtered_reminders = filtered_reminders[filtered_reminders['Acknowledged (Yes/No)'] == True]
        elif selected_status == "Sent but Not Acknowledged":
            filtered_reminders = filtered_reminders[
                (filtered_reminders['Reminder Sent (Yes/No)'] == True) & 
                (filtered_reminders['Acknowledged (Yes/No)'] == False)
            ]
        
        if len(filtered_reminders) == 0:
            st.error("No data available with the selected filters")
    
    # Main content
    if len(filtered_reminders) > 0:
        # Key metrics
        st.header("Reminder System Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        reminder_stats = data_processor.get_reminder_stats(filtered_reminders)
        
        with col1:
            st.metric(
                "Total Reminders", 
                len(filtered_reminders),
                delta=None
            )
        
        with col2:
            st.metric(
                "Reminder Sent Rate", 
                f"{reminder_stats['sent_rate']:.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "Acknowledgment Rate", 
                f"{reminder_stats['ack_rate']:.1f}%",
                delta=None
            )
        
        with col4:
            missed_rate = 100 - reminder_stats['ack_rate'] if not pd.isna(reminder_stats['ack_rate']) else 0
            st.metric(
                "Missed Reminder Rate", 
                f"{missed_rate:.1f}%",
                delta=None,
                delta_color="inverse"
            )
        
        # Reminder type analysis
        st.header("Reminder Type Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Reminder type distribution
            type_counts = filtered_reminders['Reminder Type'].value_counts()
            type_fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Reminder Type Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(type_fig, use_container_width=True)
        
        with col2:
            # Acknowledgment rate by type
            sent_reminders = filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True]
            
            if not sent_reminders.empty:
                ack_by_type = sent_reminders.groupby(
                    'Reminder Type'
                )['Acknowledged (Yes/No)'].mean() * 100
                
                # Convert Series to DataFrame for plotly express
                ack_df = ack_by_type.reset_index()
                ack_df.columns = ['Reminder Type', 'Acknowledgment Rate']
                
                ack_fig = px.bar(
                    ack_df,
                    x='Reminder Type',
                    y='Acknowledgment Rate',
                    title="Acknowledgment Rate by Reminder Type",
                    color='Reminder Type'
                )
                
                ack_fig.update_layout(yaxis=dict(range=[0, 100]))
                st.plotly_chart(ack_fig, use_container_width=True)
            else:
                st.info("No sent reminders data available for acknowledgment rate analysis.")
        
        # Reminder time analysis
        st.header("Reminder Timing Analysis")
        
        # Extract hour directly from time objects
        filtered_reminders['Hour'] = filtered_reminders['Scheduled Time'].apply(lambda x: x.hour)
        
        # Reminders by hour
        hour_counts = filtered_reminders.groupby('Hour').size().reset_index(name='Count')
        
        hour_fig = px.bar(
            hour_counts,
            x='Hour',
            y='Count',
            title="Reminders by Hour of Day",
            labels={'Hour': 'Hour of Day', 'Count': 'Number of Reminders'}
        )
        
        hour_fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(24)),
                ticktext=[f"{i}:00" for i in range(24)]
            )
        )
        
        st.plotly_chart(hour_fig, use_container_width=True)
        
        # Effectiveness by hour
        if len(filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True]) > 0:
            ack_by_hour = filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True].groupby(
                'Hour'
            )['Acknowledged (Yes/No)'].mean() * 100
            
            # Convert Series to DataFrame for plotly express
            ack_hour_df = pd.DataFrame({
                'Hour': ack_by_hour.index,
                'Acknowledgment Rate': ack_by_hour.values
            })
            
            ack_hour_fig = px.line(
                ack_hour_df,
                x='Hour',
                y='Acknowledgment Rate',
                title="Reminder Effectiveness by Hour",
                markers=True
            )
            
            ack_hour_fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(24)),
                    ticktext=[f"{i}:00" for i in range(24)]
                ),
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(ack_hour_fig, use_container_width=True)
        
        # Reminder compliance over time
        st.header("Reminder Compliance Trend")
        
        # Prepare data for trend
        filtered_reminders = filtered_reminders.sort_values('Timestamp')
        filtered_reminders['Date'] = filtered_reminders['Timestamp'].dt.date
        
        # Only include dates with sent reminders
        sent_by_date = filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True].groupby(
            'Date'
        ).size().reset_index(name='Sent')
        
        ack_by_date = filtered_reminders[
            (filtered_reminders['Reminder Sent (Yes/No)'] == True) & 
            (filtered_reminders['Acknowledged (Yes/No)'] == True)
        ].groupby('Date').size().reset_index(name='Acknowledged')
        
        # Merge
        trend_data = pd.merge(sent_by_date, ack_by_date, on='Date', how='left')
        trend_data['Acknowledged'] = trend_data['Acknowledged'].fillna(0)
        trend_data['Compliance Rate'] = (trend_data['Acknowledged'] / trend_data['Sent']) * 100
        
        # Create trend figure
        trend_fig = px.line(
            trend_data,
            x='Date',
            y='Compliance Rate',
            title="Reminder Compliance Rate Over Time",
            labels={'Date': 'Date', 'Compliance Rate': 'Compliance Rate (%)'},
            markers=True
        )
        
        trend_fig.update_layout(yaxis=dict(range=[0, 100]))
        
        st.plotly_chart(trend_fig, use_container_width=True)
        
        # Reminder effectiveness by type and time
        st.header("Reminder Effectiveness by Type and Time")
        
        # Create heatmap
        if len(filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True]) > 0:
            heatmap_data = filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True].groupby(
                ['Reminder Type', 'Hour']
            )['Acknowledged (Yes/No)'].mean() * 100
            
            heatmap_data = heatmap_data.reset_index()
            heatmap_pivot = heatmap_data.pivot(
                index='Reminder Type', 
                columns='Hour', 
                values='Acknowledged (Yes/No)'
            ).fillna(0)
            
            heatmap_fig = px.imshow(
                heatmap_pivot,
                labels=dict(x="Hour of Day", y="Reminder Type", color="Acknowledgment Rate (%)"),
                x=[f"{i}:00" for i in range(24)],
                y=heatmap_pivot.index,
                color_continuous_scale="RdYlGn",
                range_color=[0, 100]
            )
            
            st.plotly_chart(heatmap_fig, use_container_width=True)
        
        # User-specific compliance
        if selected_device != 'All':
            st.header(f"Reminder Compliance for {selected_device}")
            
            # Create compliance chart by reminder type
            user_compliance = filtered_reminders[filtered_reminders['Reminder Sent (Yes/No)'] == True].groupby(
                'Reminder Type'
            )['Acknowledged (Yes/No)'].mean() * 100
            
            # Convert Series to DataFrame for plotly express
            user_comp_df = pd.DataFrame({
                'Reminder Type': user_compliance.index,
                'Compliance Rate': user_compliance.values
            })
            
            user_comp_fig = px.bar(
                user_comp_df,
                x='Reminder Type',
                y='Compliance Rate',
                title=f"Compliance Rate by Reminder Type for {selected_device}",
                color='Reminder Type'
            )
            
            user_comp_fig.update_layout(yaxis=dict(range=[0, 100]))
            st.plotly_chart(user_comp_fig, use_container_width=True)
        
        # Create a new reminder (interface only)
        st.header("Reminder Management")
        
        with st.expander("Create New Reminder"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_device = st.selectbox("Device/User ID", device_options)
            
            with col2:
                new_type = st.selectbox("Reminder Type", reminder_types)
            
            with col3:
                new_time = st.time_input("Scheduled Time", datetime.now().time())
            
            if st.button("Create Reminder"):
                st.success(f"Reminder would be created for {new_device} of type {new_type} at {new_time}")
                st.info("Note: This is a UI demonstration. In a production system, this would save to the database.")
        
        # Raw data table
        st.header("Reminders Data")
        st.dataframe(
            filtered_reminders[[
                'Device-ID/User-ID', 'Timestamp', 'Reminder Type', 
                'Scheduled Time', 'Reminder Sent (Yes/No)', 'Acknowledged (Yes/No)'
            ]],
            use_container_width=True
        )
    else:
        st.warning("No reminder data available for the selected filters.")

# Run the app
if __name__ == "__main__":
    main()
