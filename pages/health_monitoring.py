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
    page_title="Health Monitoring - Elderly Care System",
    page_icon="❤️",
    layout="wide"
)

# Initialize session state if needed
if 'health_data' not in st.session_state:
    st.warning("Please return to the main dashboard to load data first.")
    st.stop()

def main():
    # Header
    st.title("📊 Health Monitoring Dashboard")
    st.write("Comprehensive health metrics tracking and analysis for elderly care")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # User/Device filter
        device_options = ['All'] + sorted(st.session_state.health_data['Device-ID/User-ID'].unique().tolist())
        selected_device = st.selectbox("Select Device/User", device_options)
        
        # Date range filter
        min_date = st.session_state.health_data['Timestamp'].dt.date.min()
        max_date = st.session_state.health_data['Timestamp'].dt.date.max()
        
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
        
        # Apply filters
        filtered_health = st.session_state.health_data.copy()
        
        if selected_device != 'All':
            filtered_health = filtered_health[filtered_health['Device-ID/User-ID'] == selected_device]
        
        filtered_health = filtered_health[
            (filtered_health['Timestamp'].dt.date >= start_date) & 
            (filtered_health['Timestamp'].dt.date <= end_date)
        ]
        
        # View alert-only option
        show_alerts_only = st.checkbox("Show Alert Events Only")
        if show_alerts_only:
            filtered_health = filtered_health[filtered_health['Alert Triggered (Yes/No)'] == 'Yes']
        
        if len(filtered_health) == 0:
            st.error("No data available with the selected filters")
    
    # Main content
    if len(filtered_health) > 0:
        # Key metrics
        st.header("Key Health Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        health_stats = data_processor.get_health_stats(filtered_health)
        
        with col1:
            st.metric(
                "Abnormal Heart Rate", 
                f"{health_stats['abnormal_hr']}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Abnormal Blood Pressure", 
                f"{health_stats['abnormal_bp']}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "Abnormal Glucose", 
                f"{health_stats['abnormal_glucose']}%",
                delta=None
            )
        
        with col4:
            st.metric(
                "Low SpO₂", 
                f"{health_stats['low_spo2']}%",
                delta=None
            )
        
        # Health metrics visualization
        st.header("Health Metrics Visualization")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Heart Rate", "Blood Pressure", "Glucose Levels", "Oxygen Saturation"
        ])
        
        with tab1:
            # Heart Rate
            st.subheader("Heart Rate Monitoring")
            
            # Heart rate over time
            hr_fig = go.Figure()
            
            hr_fig.add_trace(go.Scatter(
                x=filtered_health['Timestamp'],
                y=filtered_health['Heart Rate'],
                mode='lines+markers',
                name='Heart Rate',
                marker=dict(
                    color=filtered_health['Heart Rate Below/Above Threshold (Yes/No)'].map({
                        'Yes': 'red', 'No': 'blue'
                    })
                )
            ))
            
            hr_fig.update_layout(
                title="Heart Rate Over Time",
                xaxis_title="Date/Time",
                yaxis_title="Heart Rate (bpm)",
                height=400
            )
            
            st.plotly_chart(hr_fig, use_container_width=True)
            
            # Heart rate distribution
            hr_dist = px.histogram(
                filtered_health, 
                x="Heart Rate",
                color="Heart Rate Below/Above Threshold (Yes/No)",
                color_discrete_map={'Yes': 'red', 'No': 'blue'},
                title="Heart Rate Distribution"
            )
            
            st.plotly_chart(hr_dist, use_container_width=True)
        
        with tab2:
            # Blood Pressure
            st.subheader("Blood Pressure Monitoring")
            
            # BP over time
            bp_fig = go.Figure()
            
            bp_fig.add_trace(go.Scatter(
                x=filtered_health['Timestamp'],
                y=filtered_health['Systolic'],
                mode='lines+markers',
                name='Systolic',
                line=dict(color='royalblue')
            ))
            
            bp_fig.add_trace(go.Scatter(
                x=filtered_health['Timestamp'],
                y=filtered_health['Diastolic'],
                mode='lines+markers',
                name='Diastolic',
                line=dict(color='lightblue')
            ))
            
            bp_fig.update_layout(
                title="Blood Pressure Over Time",
                xaxis_title="Date/Time",
                yaxis_title="Blood Pressure (mmHg)",
                height=400
            )
            
            st.plotly_chart(bp_fig, use_container_width=True)
            
            # BP scatter plot
            bp_scatter = px.scatter(
                filtered_health,
                x="Systolic",
                y="Diastolic",
                color="Blood Pressure Below/Above Threshold (Yes/No)",
                color_discrete_map={'Yes': 'red', 'No': 'blue'},
                title="Blood Pressure Readings",
                labels={"Systolic": "Systolic (mmHg)", "Diastolic": "Diastolic (mmHg)"}
            )
            
            # Add normal range rectangle
            bp_scatter.add_shape(
                type="rect",
                x0=90, y0=60,
                x1=120, y1=80,
                line=dict(
                    color="green",
                    width=1,
                ),
                fillcolor="rgba(0,255,0,0.1)",
                layer="below"
            )
            
            bp_scatter.add_annotation(
                x=105, y=70,
                text="Normal Range",
                showarrow=False,
                font=dict(size=10, color="green")
            )
            
            st.plotly_chart(bp_scatter, use_container_width=True)
        
        with tab3:
            # Glucose Levels
            st.subheader("Glucose Monitoring")
            
            # Glucose over time
            glucose_fig = go.Figure()
            
            glucose_fig.add_trace(go.Scatter(
                x=filtered_health['Timestamp'],
                y=filtered_health['Glucose Levels'],
                mode='lines+markers',
                name='Glucose',
                marker=dict(
                    color=filtered_health['Glucose Levels Below/Above Threshold (Yes/No)'].map({
                        'Yes': 'red', 'No': 'green'
                    })
                )
            ))
            
            # Add reference lines
            glucose_fig.add_shape(
                type="line",
                x0=filtered_health['Timestamp'].min(),
                x1=filtered_health['Timestamp'].max(),
                y0=70, y1=70,
                line=dict(color="orange", width=1, dash="dash")
            )
            
            glucose_fig.add_shape(
                type="line",
                x0=filtered_health['Timestamp'].min(),
                x1=filtered_health['Timestamp'].max(),
                y0=140, y1=140,
                line=dict(color="orange", width=1, dash="dash")
            )
            
            glucose_fig.update_layout(
                title="Glucose Levels Over Time",
                xaxis_title="Date/Time",
                yaxis_title="Glucose (mg/dL)",
                height=400
            )
            
            st.plotly_chart(glucose_fig, use_container_width=True)
            
            # Glucose distribution
            glucose_dist = px.histogram(
                filtered_health, 
                x="Glucose Levels",
                color="Glucose Levels Below/Above Threshold (Yes/No)",
                color_discrete_map={'Yes': 'red', 'No': 'green'},
                title="Glucose Level Distribution"
            )
            
            st.plotly_chart(glucose_dist, use_container_width=True)
        
        with tab4:
            # Oxygen Saturation
            st.subheader("Oxygen Saturation (SpO₂) Monitoring")
            
            # SpO₂ over time
            spo2_fig = go.Figure()
            
            spo2_fig.add_trace(go.Scatter(
                x=filtered_health['Timestamp'],
                y=filtered_health['Oxygen Saturation (SpO₂%)'],
                mode='lines+markers',
                name='SpO₂',
                marker=dict(
                    color=filtered_health['SpO₂ Below Threshold (Yes/No)'].map({
                        'Yes': 'red', 'No': 'purple'
                    })
                )
            ))
            
            # Add reference line
            spo2_fig.add_shape(
                type="line",
                x0=filtered_health['Timestamp'].min(),
                x1=filtered_health['Timestamp'].max(),
                y0=90, y1=90,
                line=dict(color="red", width=1, dash="dash")
            )
            
            spo2_fig.update_layout(
                title="Oxygen Saturation Over Time",
                xaxis_title="Date/Time",
                yaxis_title="SpO₂ (%)",
                height=400
            )
            
            st.plotly_chart(spo2_fig, use_container_width=True)
            
            # SpO₂ distribution
            spo2_dist = px.histogram(
                filtered_health, 
                x="Oxygen Saturation (SpO₂%)",
                color="SpO₂ Below Threshold (Yes/No)",
                color_discrete_map={'Yes': 'red', 'No': 'purple'},
                title="Oxygen Saturation Distribution"
            )
            
            st.plotly_chart(spo2_dist, use_container_width=True)
        
        # Health Timeline
        st.header("Health Metrics Timeline")
        if selected_device != 'All':
            timeline_fig = visualization.plot_health_timeline(filtered_health, selected_device)
        else:
            st.info("Please select a specific user/device to view the health timeline")
            timeline_fig = None
        
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        # Correlation Analysis
        st.header("Correlation Analysis")
        corr_fig = visualization.plot_health_metrics_correlation(filtered_health)
        st.plotly_chart(corr_fig, use_container_width=True)
        
        # Data table
        st.header("Health Monitoring Data")
        st.dataframe(
            filtered_health[[
                'Device-ID/User-ID', 'Timestamp', 'Heart Rate', 'Blood Pressure',
                'Glucose Levels', 'Oxygen Saturation (SpO₂%)', 'Alert Triggered (Yes/No)'
            ]],
            use_container_width=True
        )
    else:
        st.warning("No health data available for the selected filters.")

# Run the app
if __name__ == "__main__":
    main()
