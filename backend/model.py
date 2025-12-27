import joblib
import pandas as pd
import numpy as np

class LoanPredictionModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load all model files"""
        try:
            self.model = joblib.load('model_files/model.pkl')
            self.scaler = joblib.load('model_files/scaler.pkl')
            self.label_encoders = joblib.load('model_files/label_encoders.pkl')
            self.feature_names = joblib.load('model_files/feature_names.pkl')
            # print(f" Best_Model type: {type(self.model).__name__}")
            return True
        except Exception as e:
            print(f" Error loading model files: {e}")
            return False
    
    def preprocess_data(self, data):
        """Preprocess input data for prediction"""
        try:
            # Convert to DataFrame if dict
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = data.copy()
            
            # Encode categorical variables
            for col, encoder in self.label_encoders.items():
                if col in df.columns:
                    try:
                        df[col] = encoder.transform(df[col].astype(str))
                    except ValueError as e:
                        print(f" Warning: Unknown category in {col}, using default")
                        # Handle unknown categories by using the first class
                        df[col] = 0
            
            # Ensure all features are present in correct order
            for feature in self.feature_names:
                if feature not in df.columns:
                    df[feature] = 0
            
            # Reorder columns to match training
            df = df[self.feature_names]
            
            # Scale features
            df_scaled = self.scaler.transform(df)
            
            return df_scaled
            
        except Exception as e:
            print(f" Preprocessing error: {e}")
            raise
    
    def predict_single(self, data):
        """Make prediction for single application"""
        try:
            X = self.preprocess_data(data)
            prediction = int(self.model.predict(X)[0])
            probability = float(self.model.predict_proba(X)[0][1])
            
            return {
                'prediction': prediction,
                'probability': probability,
                'status': 'Approved' if prediction == 1 else 'Rejected'
            }
        except Exception as e:
            print(f" Prediction error: {e}")
            raise
    
    def predict_batch(self, dataframe):
        """Make predictions for batch of applications"""
        try:
            results = []
            
            for idx, row in dataframe.iterrows():
                try:
                    X = self.preprocess_data(row.to_dict())
                    prediction = int(self.model.predict(X)[0])
                    probability = float(self.model.predict_proba(X)[0][1])
                    
                    results.append({
                        'row_number': idx + 1,
                        'prediction': prediction,
                        'probability': probability,
                        'status': 'Approved' if prediction == 1 else 'Rejected'
                    })
                except Exception as e:
                    results.append({
                        'row_number': idx + 1,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            print(f" Batch prediction error: {e}")
            raise


# Test the model loading
if __name__ == "__main__":
    predictor = LoanPredictionModel()
    
    if predictor.model:
        print("\nModel loaded successfully!")
        
        # Example for Testing Model locally
        
        Sample_predict = {
            'annual_income': 8500000,
            'debt_to_income_ratio': 0.22,
            'credit_score': 810,
            'loan_amount': 3000000,
            'interest_rate': 5.8,
            'gender': 'Female',
            'marital_status': 'Married',
            'education_level': "Bachelor's",
            'employment_status': 'Employed',
            'loan_purpose': 'Car',
            'grade_subgrade': 'A1'
        }
        result = predictor.predict_single(Sample_predict)
        
        print(f"Prediction: {result['prediction']}")
        print(f"Probability: {result['probability']:.2%}")
        print(f"Output: \n {result}")
    else:
        print("\n Model loading failed!")