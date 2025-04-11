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
    page_title="Safety Monitoring - Elderly Care System",
    page_icon="🛡️",
    layout="wide"
)

# Initialize session state if needed
if 'safety_data' not in st.session_state:
    st.warning("Please return to the main dashboard to load data first.")
    st.stop()

def main():
    # Header
    st.title("🛡️ Safety Monitoring Dashboard")
    st.write("Fall detection and movement tracking for elderly care")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # User/Device filter
        device_options = ['All'] + sorted(st.session_state.safety_data['Device-ID/User-ID'].unique().tolist())
        selected_device = st.selectbox("Select Device/User", device_options)
        
        # Date range filter
        min_date = st.session_state.safety_data['Timestamp'].dt.date.min()
        max_date = st.session_state.safety_data['Timestamp'].dt.date.max()
        
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
        
        # Location filter
        locations = st.session_state.safety_data['Location'].unique().tolist()
        selected_locations = st.multiselect(
            "Filter by Location",
            options=locations,
            default=locations
        )
        
        # Movement type filter
        movement_types = st.session_state.safety_data['Movement Activity'].unique().tolist()
        selected_movements = st.multiselect(
            "Filter by Movement Type",
            options=movement_types,
            default=movement_types
        )
        
        # Fall detection filter
        show_falls_only = st.checkbox("Show Falls Only")
        
        # Apply filters
        filtered_safety = st.session_state.safety_data.copy()
        
        if selected_device != 'All':
            filtered_safety = filtered_safety[filtered_safety['Device-ID/User-ID'] == selected_device]
        
        filtered_safety = filtered_safety[
            (filtered_safety['Timestamp'].dt.date >= start_date) & 
            (filtered_safety['Timestamp'].dt.date <= end_date)
        ]
        
        if selected_locations:
            filtered_safety = filtered_safety[filtered_safety['Location'].isin(selected_locations)]
        
        if selected_movements:
            filtered_safety = filtered_safety[filtered_safety['Movement Activity'].isin(selected_movements)]
        
        if show_falls_only:
            filtered_safety = filtered_safety[filtered_safety['Fall Detected (Yes/No)'] == True]
        
        if len(filtered_safety) == 0:
            st.error("No data available with the selected filters")
    
    # Main content
    if len(filtered_safety) > 0:
        # Key metrics
        st.header("Key Safety Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        safety_stats = data_processor.get_safety_stats(filtered_safety)
        
        with col1:
            st.metric(
                "Total Fall Incidents", 
                safety_stats['fall_count'],
                delta=None
            )
        
        with col2:
            st.metric(
                "High Impact Falls", 
                safety_stats['high_impact_falls'],
                delta=None
            )
        
        with col3:
            st.metric(
                "Avg. Inactivity Duration", 
                f"{safety_stats['avg_inactivity_duration']:.1f} sec",
                delta=None
            )
        
        with col4:
            st.metric(
                "Safety Alerts Triggered", 
                safety_stats['alerts_triggered'],
                delta=None
            )
        
        # Falls Map
        st.header("Fall Incident Analysis")
        
        # Falls by location
        falls_by_location = filtered_safety[filtered_safety['Fall Detected (Yes/No)'] == True]['Location'].value_counts()
        
        if len(falls_by_location) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Falls by Location")
                falls_loc_fig = px.pie(
                    values=falls_by_location.values,
                    names=falls_by_location.index,
                    title="Fall Incidents by Location",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                st.plotly_chart(falls_loc_fig, use_container_width=True)
            
            with col2:
                st.subheader("Falls by Impact Level")
                falls_impact = filtered_safety[filtered_safety['Fall Detected (Yes/No)'] == True]['Impact Force Level'].value_counts()
                falls_impact_fig = px.bar(
                    x=falls_impact.index,
                    y=falls_impact.values,
                    title="Falls by Impact Level",
                    color=falls_impact.index,
                    color_discrete_map={
                        'Low': 'green',
                        'Medium': 'orange',
                        'High': 'red'
                    }
                )
                st.plotly_chart(falls_impact_fig, use_container_width=True)
            
            # Fall incidents over time
            st.subheader("Fall Incidents Over Time")
            falls_data = filtered_safety[filtered_safety['Fall Detected (Yes/No)'] == True].copy()
            falls_data['Date'] = falls_data['Timestamp'].dt.date
            falls_by_date = falls_data.groupby('Date').size().reset_index(name='Falls')
            
            falls_time_fig = px.line(
                falls_by_date,
                x="Date",
                y="Falls",
                title="Fall Incidents by Date",
                markers=True
            )
            st.plotly_chart(falls_time_fig, use_container_width=True)
            
            # Fall details table
            st.subheader("Fall Incidents Details")
            st.dataframe(
                falls_data[[
                    'Device-ID/User-ID', 'Timestamp', 'Location', 'Impact Force Level',
                    'Post-Fall Inactivity Duration (Seconds)', 'Alert Triggered (Yes/No)', 
                    'Caregiver Notified (Yes/No)'
                ]],
                use_container_width=True
            )
        else:
            st.info("No fall incidents recorded with the current filters.")
        
        # Movement patterns analysis
        st.header("Movement Patterns Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Movement types distribution
            movement_counts = filtered_safety['Movement Activity'].value_counts()
            movement_fig = px.pie(
                values=movement_counts.values,
                names=movement_counts.index,
                title="Movement Activity Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(movement_fig, use_container_width=True)
        
        with col2:
            # Location distribution
            location_counts = filtered_safety['Location'].value_counts()
            location_fig = px.bar(
                x=location_counts.index,
                y=location_counts.values,
                title="Activity by Location",
                color=location_counts.index
            )
            st.plotly_chart(location_fig, use_container_width=True)
        
        # Movement patterns by time of day
        st.subheader("Movement Patterns by Time of Day")
        filtered_safety['Hour'] = filtered_safety['Timestamp'].dt.hour
        
        # Group by hour and movement type
        hourly_movement = filtered_safety.groupby(['Hour', 'Movement Activity']).size().reset_index(name='Count')
        
        hourly_fig = px.line(
            hourly_movement,
            x="Hour",
            y="Count",
            color="Movement Activity",
            title="Movement Patterns Throughout the Day",
            markers=True
        )
        
        hourly_fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(24)),
                ticktext=[f"{i}:00" for i in range(24)]
            )
        )
        
        st.plotly_chart(hourly_fig, use_container_width=True)
        
        # Movement heatmap
        st.subheader("Activity Heatmap by Location and Time")
        
        # Create hour-location heatmap
        heatmap_data = filtered_safety.groupby(['Hour', 'Location']).size().reset_index(name='Count')
        heatmap_pivot = heatmap_data.pivot(index='Location', columns='Hour', values='Count').fillna(0)
        
        heatmap_fig = px.imshow(
            heatmap_pivot,
            labels=dict(x="Hour of Day", y="Location", color="Activity Count"),
            x=[f"{i}:00" for i in range(24)],
            y=heatmap_pivot.index,
            color_continuous_scale="Viridis"
        )
        
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        # Safety Timeline
        if selected_device != 'All':
            st.header(f"Safety Timeline for {selected_device}")
            
            # Create timeline of activity and falls
            timeline_data = filtered_safety.sort_values('Timestamp')
            
            timeline_fig = go.Figure()
            
            # Add movement activity
            for movement in movement_types:
                move_data = timeline_data[timeline_data['Movement Activity'] == movement]
                
                if len(move_data) > 0:
                    timeline_fig.add_trace(go.Scatter(
                        x=move_data['Timestamp'],
                        y=[movement] * len(move_data),
                        mode='markers',
                        name=movement,
                        marker=dict(size=10)
                    ))
            
            # Add fall incidents
            falls = timeline_data[timeline_data['Fall Detected (Yes/No)'] == True]
            
            if len(falls) > 0:
                timeline_fig.add_trace(go.Scatter(
                    x=falls['Timestamp'],
                    y=falls['Movement Activity'],
                    mode='markers',
                    name='Fall',
                    marker=dict(
                        symbol='x',
                        size=15,
                        color='red',
                        line=dict(width=2, color='black')
                    )
                ))
            
            timeline_fig.update_layout(
                title=f"Activity and Falls Timeline for {selected_device}",
                xaxis_title="Date/Time",
                yaxis_title="Activity Type",
                height=400
            )
            
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        # Raw data table
        st.header("Safety Monitoring Data")
        st.dataframe(
            filtered_safety[[
                'Device-ID/User-ID', 'Timestamp', 'Movement Activity', 'Location',
                'Fall Detected (Yes/No)', 'Impact Force Level', 'Post-Fall Inactivity Duration (Seconds)'
            ]],
            use_container_width=True
        )
    else:
        st.warning("No safety data available for the selected filters.")

# Run the app
if __name__ == "__main__":
    main()
