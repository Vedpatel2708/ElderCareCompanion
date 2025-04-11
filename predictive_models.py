import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error

class HealthRiskPredictor:
    """Predicts health deterioration risk based on monitoring data"""
    
    def __init__(self):
        self.model = None
        self.features = None
        self.trained = False
    
    def preprocess_data(self, merged_data):
        """Preprocess merged data for modeling"""
        # Select relevant features
        features = [
            'Heart Rate', 'Systolic', 'Diastolic', 'Glucose Levels', 'SpO₂',
            'Movement Activity', 'Fall Detected (Yes/No)', 
            'Reminder Sent (Yes/No)', 'Acknowledged (Yes/No)'
        ]
        
        # Get features that exist in the dataframe
        self.features = [f for f in features if f in merged_data.columns]
        
        # Create target variable (any alert triggered)
        merged_data['Risk'] = merged_data['Has Any Alert']
        
        # Prepare categorical and numerical features
        categorical_features = ['Movement Activity']
        categorical_features = [f for f in categorical_features if f in merged_data.columns]
        
        numerical_features = [f for f in self.features if f not in categorical_features]
        
        # Create preprocessing pipeline
        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Create the full pipeline with the model
        self.model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        return merged_data
    
    def train(self, merged_data):
        """Train the prediction model"""
        # Preprocess data
        data = self.preprocess_data(merged_data)
        
        # Split data
        X = data[self.features]
        y = data['Risk']
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.trained = True
            return {
                'accuracy': accuracy,
                'model_type': 'Random Forest',
                'feature_count': len(self.features)
            }
        except Exception as e:
            return {
                'error': str(e),
                'model_type': 'Random Forest',
                'feature_count': len(self.features) if self.features else 0
            }
    
    def predict_risk(self, new_data):
        """Predict risk for new data"""
        if not self.trained or self.model is None:
            # Return an empty DataFrame with required columns
            if not new_data.empty:
                result_df = new_data.copy()
            else:
                # Create a minimal dataframe with all required columns
                result_df = pd.DataFrame({
                    'Device-ID/User-ID': ['USER001'],
                    'Timestamp': [pd.Timestamp.now()],
                    'Heart Rate': [70],
                    'Blood Pressure': ['120/80'],
                    'Systolic': [120],
                    'Diastolic': [80],
                    'Glucose Levels': [100],
                    'Oxygen Saturation (SpO₂%)': [98],
                    'SpO₂': [98],
                    'Heart Rate Below/Above Threshold (Yes/No)': [False],
                    'Blood Pressure Threshold (Yes/No)': [False],
                    'Glucose Levels Below/Above Threshold (Yes/No)': [False],
                    'SpO₂ Below Threshold (Yes/No)': [False]
                })
            
            result_df['Risk_Score'] = 0
            result_df['Risk_Level'] = 'Low'
            return result_df
        
        try:
            # Create a copy to avoid modifying the original
            processed_data = new_data.copy()
            
            # Ensure data has required features
            features_present = [f for f in self.features if f in processed_data.columns]
            if len(features_present) < len(self.features):
                missing = set(self.features) - set(features_present)
                print(f"Warning: Missing features: {missing}")
                # Add missing features with NaN values
                for f in missing:
                    processed_data[f] = np.nan
            
            # Make prediction
            X = processed_data[self.features]
            probabilities = self.model.predict_proba(X)
            
            # Add risk probabilities to data
            processed_data['Risk_Score'] = probabilities[:, 1]  # Probability of class 1 (risk)
            
            # Classify risk levels
            processed_data['Risk_Level'] = pd.cut(
                processed_data['Risk_Score'], 
                bins=[0, 0.3, 0.7, 1.0], 
                labels=['Low', 'Medium', 'High']
            )
            
            return processed_data
        except Exception as e:
            print(f"Prediction error: {e}")
            # Return an empty DataFrame with required columns
            result_df = new_data.copy()
            result_df['Risk_Score'] = 0
            result_df['Risk_Level'] = 'Low'
            return result_df

class FallRiskPredictor:
    """Predicts fall risk based on past activity patterns"""
    
    def __init__(self):
        self.model = None
        self.features = None
        self.trained = False
    
    def preprocess_data(self, safety_data):
        """Preprocess safety data for fall risk prediction"""
        # Create features based on movement patterns and time
        if safety_data is None or len(safety_data) == 0:
            return None
        
        # Add time features
        safety_data['Hour'] = safety_data['Timestamp'].dt.hour
        safety_data['DayOfWeek'] = safety_data['Timestamp'].dt.dayofweek
        
        # Create target: any fall in next 24 hours
        safety_data = safety_data.sort_values(['Device-ID/User-ID', 'Timestamp'])
        safety_data['Next_Day_Fall'] = False
        
        # For each device, check if there's a fall in the next 24 hours
        for device in safety_data['Device-ID/User-ID'].unique():
            device_data = safety_data[safety_data['Device-ID/User-ID'] == device].copy()
            device_data.loc[:, 'Next_Day_Timestamp'] = device_data['Timestamp'] + pd.Timedelta(days=1)
            
            for idx, row in device_data.iterrows():
                # Check if there's a fall within the next 24 hours
                next_day = device_data[
                    (device_data['Timestamp'] > row['Timestamp']) & 
                    (device_data['Timestamp'] <= row['Next_Day_Timestamp'])
                ]
                
                if len(next_day) > 0 and next_day['Fall Detected (Yes/No)'].any():
                    safety_data.loc[idx, 'Next_Day_Fall'] = True
        
        # Select features
        self.features = [
            'Hour', 'DayOfWeek', 'Movement Activity',
            'Location'
        ]
        
        return safety_data
    
    def train(self, safety_data):
        """Train the fall risk prediction model"""
        # Preprocess data
        data = self.preprocess_data(safety_data)
        if data is None:
            return {'error': 'No valid safety data for training'}
        
        # Prepare features and target
        X = pd.get_dummies(data[self.features], drop_first=True)
        y = data['Next_Day_Fall']
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
            
            # Create and train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.trained = True
            return {
                'accuracy': accuracy,
                'model_type': 'Random Forest',
                'feature_count': X.shape[1]
            }
        except Exception as e:
            return {
                'error': str(e),
                'model_type': 'Random Forest',
                'feature_count': 0
            }
    
    def predict_fall_risk(self, new_data):
        """Predict fall risk for new data"""
        if not self.trained or self.model is None:
            # Return an empty DataFrame with required columns
            if not new_data.empty:
                result_df = new_data.copy()
            else:
                # Create a minimal dataframe with all required columns
                result_df = pd.DataFrame({
                    'Device-ID/User-ID': ['USER001'],
                    'Timestamp': [pd.Timestamp.now()],
                    'Movement Activity': ['Walking'],
                    'Fall Detected (Yes/No)': [False],
                    'Impact Force Level': ['None'],
                    'Post Fall Inactivity (minutes)': [0],
                    'Location': ['Living Room']
                })
            
            result_df['Fall_Risk_Score'] = 0
            result_df['Fall_Risk_Level'] = 'Low'
            return result_df
        
        try:
            # Create a copy to avoid modifying the original
            processed_data = new_data.copy()
            
            # Add time features
            processed_data['Hour'] = processed_data['Timestamp'].dt.hour
            processed_data['DayOfWeek'] = processed_data['Timestamp'].dt.dayofweek
            
            # Prepare features
            X = pd.get_dummies(processed_data[self.features], drop_first=True)
            
            # Ensure test data has the same columns as training data
            missing_cols = set(self.model.feature_names_in_) - set(X.columns)
            for col in missing_cols:
                X[col] = 0
            X = X[self.model.feature_names_in_]
            
            # Make prediction
            probabilities = self.model.predict_proba(X)
            
            # Add risk scores to data
            processed_data['Fall_Risk_Score'] = probabilities[:, 1]  # Probability of class 1 (fall)
            
            # Classify risk levels
            processed_data['Fall_Risk_Level'] = pd.cut(
                processed_data['Fall_Risk_Score'], 
                bins=[0, 0.3, 0.6, 1.0], 
                labels=['Low', 'Medium', 'High']
            )
            
            return processed_data
        except Exception as e:
            print(f"Fall prediction error: {e}")
            # Return an empty DataFrame with required columns
            result_df = new_data.copy()
            result_df['Fall_Risk_Score'] = 0
            result_df['Fall_Risk_Level'] = 'Low'
            return result_df

class ReminderEffectivenessPredictor:
    """Predicts the effectiveness of reminders based on past behavior"""
    
    def __init__(self):
        self.model = None
        self.features = None
        self.trained = False
    
    def preprocess_data(self, reminder_data):
        """Preprocess reminder data for effectiveness prediction"""
        if reminder_data is None or len(reminder_data) == 0:
            return None
        
        # Add time features
        reminder_data['Hour'] = pd.to_datetime(reminder_data['Scheduled Time'], format='%H:%M:%S').dt.hour
        reminder_data['DayOfWeek'] = reminder_data['Timestamp'].dt.dayofweek
        
        # Create features for reminder type
        reminder_type_dummies = pd.get_dummies(reminder_data['Reminder Type'], prefix='Type')
        reminder_data = pd.concat([reminder_data, reminder_type_dummies], axis=1)
        
        # Target: whether the reminder was acknowledged
        reminder_data['Effective'] = reminder_data['Acknowledged (Yes/No)']
        
        # Select features
        self.features = [
            'Hour', 'DayOfWeek', 'Type_Medication', 'Type_Appointment', 
            'Type_Exercise', 'Type_Hydration'
        ]
        
        # Keep only features that exist in the dataframe
        self.features = [f for f in self.features if f in reminder_data.columns]
        
        return reminder_data
    
    def train(self, reminder_data):
        """Train the reminder effectiveness prediction model"""
        # Preprocess data
        data = self.preprocess_data(reminder_data)
        if data is None:
            return {'error': 'No valid reminder data for training'}
        
        # Keep only reminders that were sent
        data = data[data['Reminder Sent (Yes/No)'] == True]
        if len(data) == 0:
            return {'error': 'No sent reminders in the data'}
        
        # Prepare features and target
        X = data[self.features]
        y = data['Effective']
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
            
            # Create and train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.trained = True
            return {
                'accuracy': accuracy,
                'model_type': 'Random Forest',
                'feature_count': len(self.features)
            }
        except Exception as e:
            return {
                'error': str(e),
                'model_type': 'Random Forest',
                'feature_count': len(self.features) if self.features else 0
            }
    
    def predict_effectiveness(self, new_data):
        """Predict reminder effectiveness for new data"""
        if not self.trained or self.model is None:
            # Return an empty DataFrame with required columns
            if not new_data.empty:
                result_df = new_data.copy()
            else:
                # Create a minimal dataframe with all required columns
                result_df = pd.DataFrame({
                    'Device-ID/User-ID': ['USER001'],
                    'Timestamp': [pd.Timestamp.now()],
                    'Reminder Type': ['Medication'],
                    'Scheduled Time': [pd.Timestamp.now().time()],
                    'Reminder Sent (Yes/No)': [True],
                    'Acknowledged (Yes/No)': [False]
                })
            
            result_df['Effectiveness_Score'] = 0
            result_df['Effectiveness_Level'] = 'Low'
            return result_df
        
        try:
            # Create a copy to avoid modifying the original
            processed_data = new_data.copy()
            
            # Add time features
            processed_data['Hour'] = pd.to_datetime(processed_data['Scheduled Time'], format='%H:%M:%S').dt.hour
            processed_data['DayOfWeek'] = processed_data['Timestamp'].dt.dayofweek
            
            # Create features for reminder type
            reminder_type_dummies = pd.get_dummies(processed_data['Reminder Type'], prefix='Type')
            processed_data = pd.concat([processed_data, reminder_type_dummies], axis=1)
            
            # Ensure all required features exist
            for f in self.features:
                if f not in processed_data.columns:
                    processed_data[f] = 0
            
            # Make prediction
            X = processed_data[self.features]
            probabilities = self.model.predict_proba(X)
            
            # Add effectiveness probabilities to data
            processed_data['Effectiveness_Score'] = probabilities[:, 1]  # Probability of being effective
            
            # Classify effectiveness levels
            processed_data['Effectiveness_Level'] = pd.cut(
                processed_data['Effectiveness_Score'], 
                bins=[0, 0.3, 0.7, 1.0], 
                labels=['Low', 'Medium', 'High']
            )
            
            return processed_data
        except Exception as e:
            print(f"Reminder effectiveness prediction error: {e}")
            # Return an empty DataFrame with required columns
            result_df = new_data.copy()
            result_df['Effectiveness_Score'] = 0
            result_df['Effectiveness_Level'] = 'Low'
            return result_df
