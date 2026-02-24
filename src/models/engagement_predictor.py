import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
from typing import Dict, Tuple, Optional


class EngagementPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.metrics_trained = {}
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        """Extract features from standardized schema"""
        features = pd.DataFrame()
        
        # Temporal features
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            features['hour'] = df['date'].dt.hour
            features['day_of_week'] = df['date'].dt.dayofweek
            features['month'] = df['date'].dt.month
            
        # Text features
        if 'title' in df.columns:
            features['title_length'] = df['title'].fillna('').astype(str).str.len()
            features['title_word_count'] = df['title'].fillna('').astype(str).str.split().str.len()
            
        if 'caption' in df.columns:
            features['caption_length'] = df['caption'].fillna('').astype(str).str.len()
            features['caption_word_count'] = df['caption'].fillna('').astype(str).str.split().str.len()
            
        # Metric features (use available metrics to predict others)
        if 'views' in df.columns:
            features['views'] = pd.to_numeric(df['views'], errors='coerce')
            
        if 'likes' in df.columns:
            features['likes'] = pd.to_numeric(df['likes'], errors='coerce')
            
        if 'comments' in df.columns:
            features['comments'] = pd.to_numeric(df['comments'], errors='coerce')
            
        # Engagement ratios
        if 'views' in features.columns and 'likes' in features.columns:
            features['like_rate'] = features['likes'] / (features['views'] + 1)
            
        if 'views' in features.columns and 'comments' in features.columns:
            features['comment_rate'] = features['comments'] / (features['views'] + 1)
            
        # Remove infinite values
        features = features.replace([np.inf, -np.inf], np.nan)
        
        return features, list(features.columns)
    
    def train(self, df: pd.DataFrame, target_metric: str = 'likes') -> Dict:
        """Train models to predict engagement metric"""
        features, feature_names = self.prepare_features(df)
        self.feature_names = feature_names
        
        # Check if target exists
        if target_metric not in df.columns:
            return {"error": f"Target metric '{target_metric}' not found in data"}
            
        target = pd.to_numeric(df[target_metric], errors='coerce')
        
        # Remove rows where target is missing
        valid_idx = target.notna() & features.notna().all(axis=1)
        X = features[valid_idx].fillna(0)
        y = target[valid_idx]
        
        if len(X) < 100:
            return {"error": "Not enough valid data to train (need at least 100 rows)"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
        }
        
        results = {}
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            results[name] = {
                'model': model,
                'mae': mae,
                'r2': r2,
                'predictions': y_pred,
                'actual': y_test
            }
        
        # Select best model by R2
        best_model_name = max(results, key=lambda x: results[x]['r2'])
        
        self.models[target_metric] = results[best_model_name]['model']
        self.scalers[target_metric] = scaler
        self.metrics_trained[target_metric] = True
        
        return {
            'target': target_metric,
            'best_model': best_model_name,
            'results': results,
            'feature_names': feature_names,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def predict(self, df: pd.DataFrame, target_metric: str = 'likes') -> pd.DataFrame:
        """Generate predictions for new data"""
        if target_metric not in self.models:
            raise ValueError(f"Model for '{target_metric}' not trained yet")
            
        features, _ = self.prepare_features(df)
        X = features.fillna(0)
        X_scaled = self.scalers[target_metric].transform(X)
        
        predictions = self.models[target_metric].predict(X_scaled)
        
        result = df.copy()
        result[f'predicted_{target_metric}'] = predictions
        
        return result
    
    def get_feature_importance(self, target_metric: str = 'likes') -> pd.DataFrame:
        """Get feature importance from trained model"""
        if target_metric not in self.models:
            return pd.DataFrame()
            
        model = self.models[target_metric]
        
        # Extract feature importance
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        else:
            return pd.DataFrame()
            
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return importance_df