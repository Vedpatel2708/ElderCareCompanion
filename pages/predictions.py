import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data_processor
import visualization
import predictive_models

# Set page config
st.set_page_config(
    page_title="Risk Predictions - Elderly Care System",
    page_icon="🔮",
    layout="wide"
)

# Initialize session state if needed
if 'health_data' not in st.session_state or 'safety_data' not in st.session_state or 'reminder_data' not in st.session_state:
    st.warning("Please return to the main dashboard to load data first.")
    st.stop()

def train_models():
    """Train predictive models and store in session state"""
    # Create merged dataset for analysis
    merged_data = data_processor.merge_data_for_analysis(
        st.session_state.health_data,
        st.session_state.safety_data,
        st.session_state.reminder_data
    )
    
    # Initialize and train health risk model
    health_model = predictive_models.HealthRiskPredictor()
    health_training_results = health_model.train(merged_data)
    
    # Initialize and train fall risk model
    fall_model = predictive_models.FallRiskPredictor()
    fall_training_results = fall_model.train(st.session_state.safety_data)
    
    # Initialize and train reminder effectiveness model
    reminder_model = predictive_models.ReminderEffectivenessPredictor()
    reminder_training_results = reminder_model.train(st.session_state.reminder_data)
    
    # Store models in session state
    st.session_state.health_model = health_model
    st.session_state.fall_model = fall_model
    st.session_state.reminder_model = reminder_model
    
    # Store training results
    st.session_state.model_results = {
        'health': health_training_results,
        'fall': fall_training_results,
        'reminder': reminder_training_results
    }
    
    return True

def generate_predictions():
    """Generate predictions using trained models"""
    with st.spinner("Generating predictions..."):
        # Health risk predictions
        if hasattr(st.session_state, 'health_model') and st.session_state.health_model.trained:
            health_predictions = st.session_state.health_model.predict_risk(st.session_state.health_data)
            st.session_state.health_predictions = health_predictions
        
        # Fall risk predictions
        if hasattr(st.session_state, 'fall_model') and st.session_state.fall_model.trained:
            fall_predictions = st.session_state.fall_model.predict_fall_risk(st.session_state.safety_data)
            st.session_state.fall_predictions = fall_predictions
        
        # Reminder effectiveness predictions
        if hasattr(st.session_state, 'reminder_model') and st.session_state.reminder_model.trained:
            reminder_predictions = st.session_state.reminder_model.predict_effectiveness(st.session_state.reminder_data)
            st.session_state.reminder_predictions = reminder_predictions
    
    return True

def main():
    # Header
    st.title("🔮 Predictive Analysis Dashboard")
    st.write("AI-powered risk prediction and early warning system for elderly care")
    
    # Sidebar
    with st.sidebar:
        st.header("Model Controls")
        
        # Train models button
        if st.button("Train Predictive Models"):
            with st.spinner("Training models... This may take a moment."):
                success = train_models()
                if success:
                    st.success("Models trained successfully!")
        
        # Generate predictions button
        if st.button("Generate New Predictions"):
            if not hasattr(st.session_state, 'health_model'):
                st.error("Please train the models first.")
            else:
                success = generate_predictions()
                if success:
                    st.success("Predictions generated successfully!")
        
        # User/Device filter for predictions
        if hasattr(st.session_state, 'health_predictions'):
            st.header("Filters")
            device_options = ['All'] + sorted(st.session_state.health_data['Device-ID/User-ID'].unique().tolist())
            selected_device = st.selectbox("Select Device/User", device_options)
            
            # Store selected device in session state
            st.session_state.selected_prediction_device = selected_device
    
    # Check if models are trained
    if not hasattr(st.session_state, 'health_model'):
        st.info("Please train the models using the button in the sidebar.")
        
        # Data overview
        st.header("Data Overview for Prediction")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Health Data Points", len(st.session_state.health_data))
        
        with col2:
            st.metric("Safety Data Points", len(st.session_state.safety_data))
        
        with col3:
            st.metric("Reminder Data Points", len(st.session_state.reminder_data))
        
        # Explain predictive models
        st.header("Predictive Models Information")
        
        st.subheader("Health Risk Predictor")
        st.write("""
        This model analyzes health metrics like heart rate, blood pressure, glucose levels, and oxygen saturation 
        to predict the risk of health deterioration. It helps identify users who might need medical attention 
        before a critical situation develops.
        """)
        
        st.subheader("Fall Risk Predictor")
        st.write("""
        Based on historical movement patterns, location data, and previous fall incidents, this model predicts 
        the likelihood of a fall in the near future. It can help caregivers implement preventive measures 
        for high-risk individuals.
        """)
        
        st.subheader("Reminder Effectiveness Predictor")
        st.write("""
        This model analyzes reminder compliance patterns to identify the most effective times and types of reminders 
        for each user. It helps optimize the reminder system to improve medication adherence and appointment attendance.
        """)
        
    else:
        # Model training results
        st.header("Model Training Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Health Risk Model")
            if 'accuracy' in st.session_state.model_results['health']:
                st.metric("Accuracy", f"{st.session_state.model_results['health']['accuracy']:.2f}")
            else:
                st.error(f"Error: {st.session_state.model_results['health'].get('error', 'Unknown error')}")
        
        with col2:
            st.subheader("Fall Risk Model")
            if 'accuracy' in st.session_state.model_results['fall']:
                st.metric("Accuracy", f"{st.session_state.model_results['fall']['accuracy']:.2f}")
            else:
                st.error(f"Error: {st.session_state.model_results['fall'].get('error', 'Unknown error')}")
        
        with col3:
            st.subheader("Reminder Effectiveness Model")
            if 'accuracy' in st.session_state.model_results['reminder']:
                st.metric("Accuracy", f"{st.session_state.model_results['reminder']['accuracy']:.2f}")
            else:
                st.error(f"Error: {st.session_state.model_results['reminder'].get('error', 'Unknown error')}")
        
        # Check if predictions exist
        if not (hasattr(st.session_state, 'health_predictions') and 
                hasattr(st.session_state, 'fall_predictions') and 
                hasattr(st.session_state, 'reminder_predictions')):
            st.info("Please generate predictions using the button in the sidebar.")
            
            # Initialize empty dataframes to prevent errors
            if not hasattr(st.session_state, 'health_predictions'):
                st.session_state.health_predictions = pd.DataFrame()
            if not hasattr(st.session_state, 'fall_predictions'):
                st.session_state.fall_predictions = pd.DataFrame()
            if not hasattr(st.session_state, 'reminder_predictions'):
                st.session_state.reminder_predictions = pd.DataFrame()
                
            # Stop rendering the rest of the page
            st.stop()
        else:
            # Get selected device from session state
            selected_device = st.session_state.get('selected_prediction_device', 'All')
            
            # Filter predictions by device if needed
            health_preds = st.session_state.health_predictions
            fall_preds = st.session_state.fall_predictions
            reminder_preds = st.session_state.reminder_predictions
            
            if selected_device != 'All':
                # Add safety checks for column existence
                if not health_preds.empty and 'Device-ID/User-ID' in health_preds.columns:
                    health_preds = health_preds[health_preds['Device-ID/User-ID'] == selected_device]
                
                if not fall_preds.empty and 'Device-ID/User-ID' in fall_preds.columns:
                    fall_preds = fall_preds[fall_preds['Device-ID/User-ID'] == selected_device]
                
                if not reminder_preds.empty and 'Device-ID/User-ID' in reminder_preds.columns:
                    reminder_preds = reminder_preds[reminder_preds['Device-ID/User-ID'] == selected_device]
            
            # Overall Risk Assessment
            st.header("Overall Risk Assessment")
            
            # Count users by risk level with safety checks
            if not health_preds.empty and 'Risk_Level' in health_preds.columns:
                health_risk_counts = health_preds['Risk_Level'].value_counts()
                if health_risk_counts.empty:
                    # Provide default counts if empty
                    health_risk_counts = pd.Series([0, 0, 0], index=['Low', 'Medium', 'High'])
            else:
                # Provide default counts if dataframe is empty
                health_risk_counts = pd.Series([0, 0, 0], index=['Low', 'Medium', 'High'])
            
            if not fall_preds.empty and 'Fall_Risk_Level' in fall_preds.columns:
                fall_risk_counts = fall_preds['Fall_Risk_Level'].value_counts()
                if fall_risk_counts.empty:
                    # Provide default counts if empty
                    fall_risk_counts = pd.Series([0, 0, 0], index=['Low', 'Medium', 'High'])
            else:
                # Provide default counts if dataframe is empty
                fall_risk_counts = pd.Series([0, 0, 0], index=['Low', 'Medium', 'High'])
            
            risk_col1, risk_col2 = st.columns(2)
            
            with risk_col1:
                # Health risk distribution
                health_risk_fig = px.pie(
                    values=health_risk_counts.values,
                    names=health_risk_counts.index,
                    title="Health Risk Distribution",
                    color=health_risk_counts.index,
                    color_discrete_map={
                        'Low': 'green',
                        'Medium': 'orange',
                        'High': 'red'
                    }
                )
                st.plotly_chart(health_risk_fig, use_container_width=True)
            
            with risk_col2:
                # Fall risk distribution
                fall_risk_fig = px.pie(
                    values=fall_risk_counts.values,
                    names=fall_risk_counts.index,
                    title="Fall Risk Distribution",
                    color=fall_risk_counts.index,
                    color_discrete_map={
                        'Low': 'green',
                        'Medium': 'orange',
                        'High': 'red'
                    }
                )
                st.plotly_chart(fall_risk_fig, use_container_width=True)
            
            # Health Risk Analysis
            st.header("Health Risk Analysis")
            
            # Health risk over time
            health_preds_sorted = health_preds.sort_values('Timestamp')
            
            # Create time series plot of risk scores
            health_risk_time_fig = px.scatter(
                health_preds_sorted,
                x='Timestamp',
                y='Risk_Score',
                color='Risk_Level',
                color_discrete_map={
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red'
                },
                title="Health Risk Scores Over Time",
                hover_data=['Device-ID/User-ID', 'Heart Rate', 'Systolic', 'Diastolic', 'Glucose Levels', 'SpO₂']
            )
            
            # Add risk level regions
            health_risk_time_fig.add_shape(
                type="rect",
                xref="paper", yref="y",
                x0=0, x1=1, y0=0.7, y1=1,
                fillcolor="rgba(255,0,0,0.1)",
                line=dict(width=0),
                layer="below"
            )
            
            health_risk_time_fig.add_shape(
                type="rect",
                xref="paper", yref="y",
                x0=0, x1=1, y0=0.3, y1=0.7,
                fillcolor="rgba(255,165,0,0.1)",
                line=dict(width=0),
                layer="below"
            )
            
            health_risk_time_fig.add_shape(
                type="rect",
                xref="paper", yref="y",
                x0=0, x1=1, y0=0, y1=0.3,
                fillcolor="rgba(0,128,0,0.1)",
                line=dict(width=0),
                layer="below"
            )
            
            st.plotly_chart(health_risk_time_fig, use_container_width=True)
            
            # High risk users
            high_risk_users = health_preds[health_preds['Risk_Level'] == 'High']
            
            if len(high_risk_users) > 0:
                st.subheader("High Health Risk Users")
                st.dataframe(
                    high_risk_users[[
                        'Device-ID/User-ID', 'Timestamp', 'Heart Rate', 'Blood Pressure',
                        'Glucose Levels', 'SpO₂', 'Risk_Score'
                    ]].sort_values('Risk_Score', ascending=False),
                    use_container_width=True
                )
            else:
                st.success("No users currently at high health risk.")
            
            # Fall Risk Analysis
            st.header("Fall Risk Analysis")
            
            # Fall risk by location
            fall_location_risk = fall_preds.groupby('Location')['Fall_Risk_Score'].mean().reset_index()
            
            fall_loc_fig = px.bar(
                fall_location_risk.sort_values('Fall_Risk_Score', ascending=False),
                x='Location',
                y='Fall_Risk_Score',
                title="Average Fall Risk by Location",
                color='Fall_Risk_Score',
                color_continuous_scale='RdYlGn_r'
            )
            
            st.plotly_chart(fall_loc_fig, use_container_width=True)
            
            # Fall risk by activity
            fall_activity_risk = fall_preds.groupby('Movement Activity')['Fall_Risk_Score'].mean().reset_index()
            
            fall_act_fig = px.bar(
                fall_activity_risk.sort_values('Fall_Risk_Score', ascending=False),
                x='Movement Activity',
                y='Fall_Risk_Score',
                title="Average Fall Risk by Activity",
                color='Fall_Risk_Score',
                color_continuous_scale='RdYlGn_r'
            )
            
            st.plotly_chart(fall_act_fig, use_container_width=True)
            
            # High fall risk users
            high_fall_risk = fall_preds[fall_preds['Fall_Risk_Level'] == 'High']
            
            if len(high_fall_risk) > 0:
                st.subheader("High Fall Risk Situations")
                st.dataframe(
                    high_fall_risk[[
                        'Device-ID/User-ID', 'Timestamp', 'Location', 'Movement Activity',
                        'Fall_Risk_Score', 'Fall_Risk_Level'
                    ]].sort_values('Fall_Risk_Score', ascending=False),
                    use_container_width=True
                )
            else:
                st.success("No high fall risk situations detected.")
            
            # Reminder Effectiveness Analysis
            st.header("Reminder Effectiveness Analysis")
            
            # Check if we have valid data
            if not reminder_preds.empty and 'Reminder Type' in reminder_preds.columns:
                # Effectiveness by type
                reminder_eff_by_type = reminder_preds.groupby('Reminder Type')['Effectiveness_Score'].mean().reset_index()
                
                if not reminder_eff_by_type.empty:
                    reminder_type_fig = px.bar(
                        reminder_eff_by_type.sort_values('Effectiveness_Score', ascending=False),
                        x='Reminder Type',
                        y='Effectiveness_Score',
                        title="Average Reminder Effectiveness by Type",
                        color='Effectiveness_Score',
                        color_continuous_scale='RdYlGn'
                    )
                    
                    st.plotly_chart(reminder_type_fig, use_container_width=True)
                else:
                    st.info("No reminder effectiveness data available for visualization.")
                
                # Effectiveness by hour - extract hour directly from time objects
                if 'Scheduled Time' in reminder_preds.columns:
                    reminder_preds['Hour'] = reminder_preds['Scheduled Time'].apply(lambda x: x.hour if hasattr(x, 'hour') else 0)
                    reminder_eff_by_hour = reminder_preds.groupby('Hour')['Effectiveness_Score'].mean().reset_index()
                else:
                    st.info("No scheduled time data available for hour analysis.")
                    # Create empty dataframe for later code to work with
                    reminder_eff_by_hour = pd.DataFrame(columns=['Hour', 'Effectiveness_Score'])
            else:
                st.info("No reminder effectiveness data available for analysis.")
                # Create empty dataframes for later code to work with
                reminder_eff_by_type = pd.DataFrame(columns=['Reminder Type', 'Effectiveness_Score'])
                reminder_eff_by_hour = pd.DataFrame(columns=['Hour', 'Effectiveness_Score'])
            
            reminder_hour_fig = px.line(
                reminder_eff_by_hour,
                x='Hour',
                y='Effectiveness_Score',
                title="Reminder Effectiveness by Hour of Day",
                markers=True
            )
            
            reminder_hour_fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(24)),
                    ticktext=[f"{i}:00" for i in range(24)]
                )
            )
            
            st.plotly_chart(reminder_hour_fig, use_container_width=True)
            
            # Low effectiveness reminders
            low_eff_reminders = reminder_preds[reminder_preds['Effectiveness_Level'] == 'Low']
            
            if len(low_eff_reminders) > 0:
                st.subheader("Low Effectiveness Reminders")
                st.dataframe(
                    low_eff_reminders[[
                        'Device-ID/User-ID', 'Reminder Type', 'Scheduled Time',
                        'Effectiveness_Score', 'Effectiveness_Level'
                    ]].sort_values('Effectiveness_Score'),
                    use_container_width=True
                )
                
                # Recommendations to improve reminder effectiveness
                st.subheader("Recommendations to Improve Reminder Effectiveness")
                
                # Find optimal hours for reminders if data exists
                if not reminder_eff_by_hour.empty and 'Hour' in reminder_eff_by_hour.columns:
                    optimal_hours = reminder_eff_by_hour.sort_values('Effectiveness_Score', ascending=False).head(3)['Hour'].tolist()
                    optimal_hours_str = ', '.join([f"{h}:00" for h in optimal_hours]) if optimal_hours else "various times"
                else:
                    optimal_hours_str = "various times"
                
                # Find optimal reminder types if data exists
                if not reminder_eff_by_type.empty and 'Reminder Type' in reminder_eff_by_type.columns:
                    optimal_types = reminder_eff_by_type.sort_values('Effectiveness_Score', ascending=False)['Reminder Type'].tolist()
                    optimal_type_str = optimal_types[0] if optimal_types else "appropriate reminder types"
                else:
                    optimal_type_str = "appropriate reminder types"
                
                st.write(f"1. Schedule important reminders around {optimal_hours_str} when responsiveness is highest.")
                st.write(f"2. Prioritize {optimal_type_str} which have the highest acknowledgment rate.")
                st.write("3. Bundle less effective reminder types with more effective ones to increase compliance.")
                st.write("4. Consider different reminder formats for low-effectiveness time slots.")
            else:
                st.success("No low effectiveness reminders detected.")
            
            # Comprehensive Risk Analysis
            if selected_device != 'All':
                st.header(f"Comprehensive Risk Analysis for {selected_device}")
                
                # Create multi-risk timeline
                risk_fig = go.Figure()
                
                # Add health risk if data exists
                if not health_preds.empty and 'Timestamp' in health_preds.columns and 'Risk_Score' in health_preds.columns:
                    health_device = health_preds.sort_values('Timestamp')
                    risk_fig.add_trace(go.Scatter(
                        x=health_device['Timestamp'],
                        y=health_device['Risk_Score'],
                        mode='lines+markers',
                        name='Health Risk',
                        line=dict(color='red', width=2)
                    ))
                
                # Add fall risk if data exists
                if not fall_preds.empty and 'Timestamp' in fall_preds.columns and 'Fall_Risk_Score' in fall_preds.columns:
                    fall_device = fall_preds.sort_values('Timestamp')
                    risk_fig.add_trace(go.Scatter(
                        x=fall_device['Timestamp'],
                        y=fall_device['Fall_Risk_Score'],
                        mode='lines+markers',
                        name='Fall Risk',
                        line=dict(color='orange', width=2)
                    ))
                
                risk_fig.update_layout(
                    title=f"Risk Timeline for {selected_device}",
                    xaxis_title="Date/Time",
                    yaxis_title="Risk Score (0-1)",
                    yaxis=dict(range=[0, 1])
                )
                
                # Only display chart if it has traces
                if len(risk_fig.data) > 0:
                    st.plotly_chart(risk_fig, use_container_width=True)
                else:
                    st.info("No risk timeline data available for this user.")
                
                # Overall risk assessment for the user
                avg_health_risk = 0
                if not health_preds.empty and 'Risk_Score' in health_preds.columns:
                    avg_health_risk = health_preds['Risk_Score'].mean()
                
                avg_fall_risk = 0
                if not fall_preds.empty and 'Fall_Risk_Score' in fall_preds.columns:
                    avg_fall_risk = fall_preds['Fall_Risk_Score'].mean()
                
                # Calculate overall risk
                overall_risk = (avg_health_risk + avg_fall_risk) / 2
                
                risk_assessment = "Low"
                if overall_risk > 0.7:
                    risk_assessment = "High"
                elif overall_risk > 0.3:
                    risk_assessment = "Medium"
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average Health Risk", f"{avg_health_risk:.2f}")
                
                with col2:
                    st.metric("Average Fall Risk", f"{avg_fall_risk:.2f}")
                
                with col3:
                    st.metric("Overall Risk Assessment", risk_assessment, 
                             delta=None, 
                             delta_color="off")
                
                # Personalized recommendations
                st.subheader("Personalized Recommendations")
                
                if risk_assessment == "High":
                    st.error("High Risk Assessment - Immediate Attention Required")
                    st.write("""
                    1. Schedule urgent care provider check-in
                    2. Increase monitoring frequency
                    3. Consider temporary assistance for daily activities
                    4. Review medication schedule and compliance
                    5. Implement additional fall prevention measures
                    """)
                elif risk_assessment == "Medium":
                    st.warning("Medium Risk Assessment - Heightened Monitoring Recommended")
                    st.write("""
                    1. Schedule regular check-ins with care provider
                    2. Review and adjust reminder schedule for optimal compliance
                    3. Evaluate home environment for safety improvements
                    4. Monitor vital signs more frequently
                    5. Encourage regular physical activity as appropriate
                    """)
                else:
                    st.success("Low Risk Assessment - Maintaining Wellness")
                    st.write("""
                    1. Continue with current care plan
                    2. Schedule routine wellness check
                    3. Maintain current reminder schedule
                    4. Encourage social engagement and activities
                    5. Periodic review of health metrics
                    """)
                
                # Export report button (demonstration only)
                if st.button("Export Detailed Risk Report"):
                    st.info("Risk report would be generated and exported for healthcare providers.")
                    st.write("Note: This is a UI demonstration. In a production system, this would generate a PDF report.")

# Run the app
if __name__ == "__main__":
    main()
