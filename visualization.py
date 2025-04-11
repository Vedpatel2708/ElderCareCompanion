import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_health_summary(health_data):
    """Create summary visualizations for health monitoring data"""
    if health_data is None or len(health_data) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No health data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Heart Rate Distribution", 
            "Blood Pressure Readings",
            "Glucose Levels", 
            "Oxygen Saturation (SpO₂)"
        )
    )
    
    # Heart Rate Distribution
    hr_bins = list(range(50, 131, 10))
    hr_counts = np.histogram(health_data['Heart Rate'], bins=hr_bins)[0]
    fig.add_trace(
        go.Bar(
            x=[f"{hr_bins[i]}-{hr_bins[i+1]}" for i in range(len(hr_bins)-1)],
            y=hr_counts,
            name="Heart Rate",
            marker_color='indianred'
        ),
        row=1, col=1
    )
    
    # Blood Pressure Scatter
    fig.add_trace(
        go.Scatter(
            x=health_data['Systolic'],
            y=health_data['Diastolic'],
            mode='markers',
            name='BP Readings',
            marker=dict(
                color=health_data['Blood Pressure Below/Above Threshold (Yes/No)'].map({'Yes': 'red', 'No': 'blue'}),
                size=8,
                opacity=0.6
            )
        ),
        row=1, col=2
    )
    
    # Add BP threshold lines
    fig.add_shape(
        type="rect", xref="x2", yref="y2",
        x0=90, y0=60, x1=120, y1=80,
        line=dict(color="green", width=2),
        fillcolor="rgba(0,255,0,0.1)",
        row=1, col=2
    )
    
    # Glucose Levels
    glucose_bins = list(range(60, 161, 10))
    glucose_counts = np.histogram(health_data['Glucose Levels'], bins=glucose_bins)[0]
    fig.add_trace(
        go.Bar(
            x=[f"{glucose_bins[i]}-{glucose_bins[i+1]}" for i in range(len(glucose_bins)-1)],
            y=glucose_counts,
            name="Glucose",
            marker_color='forestgreen'
        ),
        row=2, col=1
    )
    
    # SpO₂ Distribution
    fig.add_trace(
        go.Histogram(
            x=health_data['Oxygen Saturation (SpO₂%)'],
            nbinsx=10,
            name="SpO₂",
            marker_color='royalblue'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        width=900,
        showlegend=False,
        title_text="Health Monitoring Summary"
    )
    
    # Update axes titles
    fig.update_xaxes(title_text="Heart Rate (bpm)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    
    fig.update_xaxes(title_text="Systolic (mmHg)", row=1, col=2)
    fig.update_yaxes(title_text="Diastolic (mmHg)", row=1, col=2)
    
    fig.update_xaxes(title_text="Glucose (mg/dL)", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    
    fig.update_xaxes(title_text="SpO₂ (%)", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=2)
    
    return fig

def plot_safety_summary(safety_data):
    """Create summary visualizations for safety monitoring data"""
    if safety_data is None or len(safety_data) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No safety data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Falls by Location", 
            "Movement Activity Distribution",
            "Fall Impact Distribution", 
            "Inactivity Duration for Falls"
        ),
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ]
    )
    
    # Falls by Location
    fall_data = safety_data[safety_data['Fall Detected (Yes/No)'] == True]
    location_counts = fall_data['Location'].value_counts()
    
    if len(location_counts) > 0:
        fig.add_trace(
            go.Pie(
                labels=location_counts.index,
                values=location_counts.values,
                name="Falls by Location",
                marker=dict(colors=px.colors.qualitative.Set3),
                textinfo='percent+label'
            ),
            row=1, col=1
        )
    else:
        # For domain subplot like pie chart, we need to add a blank pie chart
        fig.add_trace(
            go.Pie(
                labels=["No Data"],
                values=[1],
                textinfo='none',
                hoverinfo='none',
                marker=dict(colors=['#E0E0E0']),
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add text annotation to the overall figure with a custom domain reference
        fig.add_annotation(
            text="No fall data available",
            x=0.25,  # Center of the first column (approximately)
            y=0.75,  # Center of the first row (approximately)
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=12)
        )
    
    # Movement Activity Distribution
    movement_counts = safety_data['Movement Activity'].value_counts()
    fig.add_trace(
        go.Bar(
            x=movement_counts.index,
            y=movement_counts.values,
            name="Movement Types",
            marker_color='lightskyblue'
        ),
        row=1, col=2
    )
    
    # Fall Impact Distribution
    if len(fall_data) > 0:
        impact_counts = fall_data['Impact Force Level'].value_counts()
        fig.add_trace(
            go.Bar(
                x=impact_counts.index,
                y=impact_counts.values,
                name="Impact Levels",
                marker_color='salmon'
            ),
            row=2, col=1
        )
    else:
        # Add a bar trace with empty data
        fig.add_trace(
            go.Bar(
                x=["No Data"],
                y=[0],
                marker_color='lightgray'
            ),
            row=2, col=1
        )
        
        # Add annotation to the specific cell using paper coordinates
        fig.add_annotation(
            text="No fall impact data available",
            x=0.25,  # Center of the first column (approximately)
            y=0.25,  # Center of the second row (approximately)
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=12)
        )
    
    # Inactivity Duration for Falls
    if len(fall_data) > 0:
        fig.add_trace(
            go.Scatter(
                x=fall_data['Timestamp'],
                y=fall_data['Post-Fall Inactivity Duration (Seconds)'],
                mode='markers',
                name='Inactivity Duration',
                marker=dict(
                    color=fall_data['Impact Force Level'].map({'Low': 'green', 'Medium': 'orange', 'High': 'red'}),
                    size=10,
                    opacity=0.7
                )
            ),
            row=2, col=2
        )
    else:
        # Add empty scatter trace
        fig.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode='markers',
                marker=dict(color='lightgray')
            ),
            row=2, col=2
        )
        
        # Add annotation using paper coordinates
        fig.add_annotation(
            text="No fall duration data available",
            x=0.75,  # Center of the second column (approximately)
            y=0.25,  # Center of the second row (approximately)
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=12)
        )
    
    # Update layout
    fig.update_layout(
        height=600,
        width=900,
        showlegend=False,
        title_text="Safety Monitoring Summary"
    )
    
    # Update axes titles
    fig.update_xaxes(title_text="Movement Type", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    
    fig.update_xaxes(title_text="Impact Level", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    
    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_yaxes(title_text="Duration (seconds)", row=2, col=2)
    
    return fig

def plot_reminder_summary(reminder_data):
    """Create summary visualizations for reminder data"""
    if reminder_data is None or len(reminder_data) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No reminder data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Reminder Types Distribution", 
            "Reminder Acknowledgment Rate by Type",
            "Reminders by Time of Day", 
            "Reminder Effectiveness Trend"
        ),
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "histogram"}, {"type": "scatter"}]
        ]
    )
    
    # Reminder Types Distribution
    type_counts = reminder_data['Reminder Type'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=type_counts.index,
            values=type_counts.values,
            name="Reminder Types",
            marker=dict(colors=px.colors.qualitative.Pastel),
            textinfo='percent+label'
        ),
        row=1, col=1
    )
    
    # Reminder Acknowledgment Rate by Type
    ack_by_type = reminder_data.groupby('Reminder Type')['Acknowledged (Yes/No)'].mean() * 100
    fig.add_trace(
        go.Bar(
            x=ack_by_type.index,
            y=ack_by_type.values,
            name="Acknowledgment Rate",
            marker_color='mediumpurple'
        ),
        row=1, col=2
    )
    
    # Reminders by Time of Day
    # Create a list of hours from the time objects
    scheduled_hours = [time_obj.hour for time_obj in reminder_data['Scheduled Time']]
    
    fig.add_trace(
        go.Histogram(
            x=scheduled_hours,
            nbinsx=24,
            name="Scheduled Times",
            marker_color='lightseagreen'
        ),
        row=2, col=1
    )
    
    # Reminder Effectiveness Trend
    reminder_data = reminder_data.sort_values('Timestamp')
    reminder_data['Rolling_Ack_Rate'] = reminder_data['Acknowledged (Yes/No)'].rolling(window=10).mean() * 100
    
    fig.add_trace(
        go.Scatter(
            x=reminder_data['Timestamp'],
            y=reminder_data['Rolling_Ack_Rate'],
            mode='lines',
            name='Acknowledgment Trend',
            line=dict(color='darkorange', width=2)
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        width=900,
        showlegend=False,
        title_text="Reminder System Summary"
    )
    
    # Update axes titles
    fig.update_xaxes(title_text="Reminder Type", row=1, col=2)
    fig.update_yaxes(title_text="Acknowledgment Rate (%)", row=1, col=2)
    
    fig.update_xaxes(title_text="Hour of Day", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    
    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_yaxes(title_text="10-day Rolling Acknowledgment Rate (%)", row=2, col=2)
    
    return fig

def plot_health_timeline(health_data, user_id=None):
    """Plot health metrics over time for a specific user"""
    if user_id:
        user_data = health_data[health_data['Device-ID/User-ID'] == user_id]
    else:
        user_data = health_data
    
    if user_data is None or len(user_data) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No health data available for this user",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Sort by timestamp
    user_data = user_data.sort_values('Timestamp')
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=(
            "Heart Rate Over Time", 
            "Blood Pressure Over Time",
            "Glucose Levels Over Time", 
            "Oxygen Saturation Over Time"
        ),
        shared_xaxes=True,
        vertical_spacing=0.1
    )
    
    # Heart Rate
    fig.add_trace(
        go.Scatter(
            x=user_data['Timestamp'],
            y=user_data['Heart Rate'],
            mode='lines+markers',
            name='Heart Rate',
            line=dict(color='crimson', width=2),
            marker=dict(
                color=user_data['Heart Rate Below/Above Threshold (Yes/No)'].map({'Yes': 'red', 'No': 'crimson'}),
                size=8
            )
        ),
        row=1, col=1
    )
    
    # Blood Pressure
    fig.add_trace(
        go.Scatter(
            x=user_data['Timestamp'],
            y=user_data['Systolic'],
            mode='lines+markers',
            name='Systolic',
            line=dict(color='royalblue', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=user_data['Timestamp'],
            y=user_data['Diastolic'],
            mode='lines+markers',
            name='Diastolic',
            line=dict(color='lightblue', width=2)
        ),
        row=2, col=1
    )
    
    # Glucose
    fig.add_trace(
        go.Scatter(
            x=user_data['Timestamp'],
            y=user_data['Glucose Levels'],
            mode='lines+markers',
            name='Glucose',
            line=dict(color='forestgreen', width=2),
            marker=dict(
                color=user_data['Glucose Levels Below/Above Threshold (Yes/No)'].map({'Yes': 'red', 'No': 'forestgreen'}),
                size=8
            )
        ),
        row=3, col=1
    )
    
    # SpO₂
    fig.add_trace(
        go.Scatter(
            x=user_data['Timestamp'],
            y=user_data['Oxygen Saturation (SpO₂%)'],
            mode='lines+markers',
            name='SpO₂',
            line=dict(color='purple', width=2),
            marker=dict(
                color=user_data['SpO₂ Below Threshold (Yes/No)'].map({'Yes': 'red', 'No': 'purple'}),
                size=8
            )
        ),
        row=4, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text=f"Health Metrics Timeline {f'for {user_id}' if user_id else ''}",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update y-axes titles
    fig.update_yaxes(title_text="Heart Rate (bpm)", row=1, col=1)
    fig.update_yaxes(title_text="Blood Pressure (mmHg)", row=2, col=1)
    fig.update_yaxes(title_text="Glucose (mg/dL)", row=3, col=1)
    fig.update_yaxes(title_text="SpO₂ (%)", row=4, col=1)
    
    # Update x-axis of the last plot
    fig.update_xaxes(title_text="Date/Time", row=4, col=1)
    
    return fig

def plot_health_metrics_correlation(health_data):
    """Create correlation matrix for health metrics"""
    if health_data is None or len(health_data) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No health data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Select numeric columns
    numeric_cols = ['Heart Rate', 'Systolic', 'Diastolic', 'Glucose Levels', 'SpO₂']
    data_for_corr = health_data[numeric_cols].copy()
    
    # Calculate correlation matrix
    corr_matrix = data_for_corr.corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu_r',
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size":12}
    ))
    
    fig.update_layout(
        title="Correlation Between Health Metrics",
        height=500,
        width=600
    )
    
    return fig

def plot_risk_predictions(prediction_data):
    """Create visualizations for risk predictions"""
    if prediction_data is None or len(prediction_data) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No prediction data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create scatter plot of risk scores by user
    fig = go.Figure()
    
    # Add scatter points
    for user in prediction_data['Device-ID/User-ID'].unique():
        user_data = prediction_data[prediction_data['Device-ID/User-ID'] == user]
        
        fig.add_trace(go.Scatter(
            x=user_data['Timestamp'],
            y=user_data['Risk_Score'],
            mode='markers',
            name=user,
            marker=dict(
                size=10,
                opacity=0.7,
                color=user_data['Risk_Level'].map({
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red'
                })
            )
        ))
    
    # Add risk level regions
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1, y0=0.7, y1=1,
        fillcolor="rgba(255,0,0,0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1, y0=0.3, y1=0.7,
        fillcolor="rgba(255,165,0,0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1, y0=0, y1=0.3,
        fillcolor="rgba(0,128,0,0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    # Add risk level labels
    fig.add_annotation(
        xref="paper", yref="y",
        x=0.01, y=0.85,
        text="High Risk",
        showarrow=False,
        font=dict(color="red")
    )
    
    fig.add_annotation(
        xref="paper", yref="y",
        x=0.01, y=0.5,
        text="Medium Risk",
        showarrow=False,
        font=dict(color="darkorange")
    )
    
    fig.add_annotation(
        xref="paper", yref="y",
        x=0.01, y=0.15,
        text="Low Risk",
        showarrow=False,
        font=dict(color="green")
    )
    
    # Update layout
    fig.update_layout(
        title="Health Risk Prediction by User",
        xaxis_title="Date/Time",
        yaxis_title="Risk Score",
        yaxis=dict(range=[0, 1]),
        legend_title="User ID",
        height=600
    )
    
    return fig
