"""
Predictive analytics for prompt performance forecasting.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Result of a prediction."""
    predicted_value: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    model_accuracy: float
    features_importance: Dict[str, float]
    prediction_horizon: str


class PredictiveAnalytics:
    """Predictive analytics for prompt performance forecasting."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
    def predict_quality_score(self, 
                            prompt_features: Dict[str, Any],
                            historical_data: List[Dict]) -> PredictionResult:
        """Predict quality score for a prompt."""
        if not historical_data:
            return self._default_prediction()
            
        # Prepare features
        X, y = self._prepare_quality_features(historical_data)
        
        if len(X) < 10:  # Need minimum data
            return self._default_prediction()
            
        # Train model
        model = self._train_quality_model(X, y)
        
        # Prepare input features
        input_features = self._extract_prompt_features(prompt_features)
        
        # Make prediction
        prediction = model.predict([input_features])[0]
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(model, X, y, input_features)
        
        # Get feature importance
        feature_importance = self._get_feature_importance(model, list(prompt_features.keys()))
        
        return PredictionResult(
            predicted_value=prediction,
            confidence_interval=confidence_interval,
            confidence_level=0.95,
            model_accuracy=self._calculate_model_accuracy(model, X, y),
            features_importance=feature_importance,
            prediction_horizon="immediate"
        )
        
    def predict_cost_trend(self,
                          prompt_id: str,
                          historical_costs: List[Dict],
                          forecast_days: int = 30) -> List[PredictionResult]:
        """Predict cost trends for a prompt over time."""
        if not historical_costs:
            return []
            
        # Prepare time series data
        df = pd.DataFrame(historical_costs)
        df['date'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('date')
        
        # Extract features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        
        # Create lag features
        df['cost_lag_1'] = df['cost_usd'].shift(1)
        df['cost_lag_7'] = df['cost_usd'].shift(7)
        
        # Remove NaN values
        df = df.dropna()
        
        if len(df) < 14:  # Need at least 2 weeks of data
            return []
            
        # Prepare features for prediction
        X = df[['day_of_week', 'month', 'day', 'cost_lag_1', 'cost_lag_7']].values
        y = df['cost_usd'].values
        
        # Train model
        model = self._train_cost_model(X, y)
        
        # Generate future dates
        last_date = df['date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
        
        predictions = []
        current_features = X[-1].copy()  # Start with last known features
        
        for i, future_date in enumerate(future_dates):
            # Update features for future date
            current_features[0] = future_date.dayofweek
            current_features[1] = future_date.month
            current_features[2] = future_date.day
            
            # Make prediction
            prediction = model.predict([current_features])[0]
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(model, X, y, current_features)
            
            predictions.append(PredictionResult(
                predicted_value=prediction,
                confidence_interval=confidence_interval,
                confidence_level=0.95,
                model_accuracy=self._calculate_model_accuracy(model, X, y),
                features_importance=self._get_feature_importance(model, ['day_of_week', 'month', 'day', 'cost_lag_1', 'cost_lag_7']),
                prediction_horizon=f"day_{i+1}"
            ))
            
            # Update lag features for next prediction
            current_features[3] = prediction  # cost_lag_1
            if i >= 6:
                current_features[4] = predictions[i-6].predicted_value  # cost_lag_7
                
        return predictions
        
    def predict_conversion_rate(self,
                               prompt_variants: List[Dict],
                               historical_data: List[Dict]) -> Dict[str, PredictionResult]:
        """Predict conversion rates for prompt variants."""
        if not historical_data or not prompt_variants:
            return {}
            
        # Prepare features
        X, y = self._prepare_conversion_features(historical_data)
        
        if len(X) < 20:  # Need more data for conversion prediction
            return {}
            
        # Train model
        model = self._train_conversion_model(X, y)
        
        predictions = {}
        
        for variant in prompt_variants:
            # Extract variant features
            variant_features = self._extract_variant_features(variant)
            
            # Make prediction
            prediction = model.predict([variant_features])[0]
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(model, X, y, variant_features)
            
            predictions[variant['name']] = PredictionResult(
                predicted_value=prediction,
                confidence_interval=confidence_interval,
                confidence_level=0.95,
                model_accuracy=self._calculate_model_accuracy(model, X, y),
                features_importance=self._get_feature_importance(model, list(variant.keys())),
                prediction_horizon="variant_comparison"
            )
            
        return predictions
        
    def predict_optimal_traffic_split(self,
                                    variants: List[Dict],
                                    historical_data: List[Dict],
                                    total_traffic: int = 1000) -> Dict[str, float]:
        """Predict optimal traffic split for A/B testing."""
        if not variants or not historical_data:
            return {}
            
        # Get conversion predictions
        conversion_predictions = self.predict_conversion_rate(variants, historical_data)
        
        if not conversion_predictions:
            return {}
            
        # Calculate optimal split using multi-armed bandit approach
        total_conversion = sum(pred.predicted_value for pred in conversion_predictions.values())
        
        if total_conversion == 0:
            # Equal split if no conversion data
            equal_split = 1.0 / len(variants)
            return {variant: equal_split for variant in conversion_predictions.keys()}
            
        # Weighted split based on predicted conversion rates
        optimal_split = {}
        for variant, prediction in conversion_predictions.items():
            optimal_split[variant] = prediction.predicted_value / total_conversion
            
        return optimal_split
        
    def _prepare_quality_features(self, historical_data: List[Dict]) -> Tuple[List[List[float]], List[float]]:
        """Prepare features for quality prediction."""
        features = []
        targets = []
        
        for data in historical_data:
            feature_vector = [
                data.get('prompt_length', 0),
                data.get('word_count', 0),
                data.get('sentence_count', 0),
                data.get('avg_word_length', 0),
                data.get('complexity_score', 0),
                data.get('specificity_score', 0),
                data.get('clarity_score', 0),
                data.get('tone_score', 0),
                data.get('context_relevance', 0),
            ]
            features.append(feature_vector)
            targets.append(data.get('quality_score', 0.5))
            
        return features, targets
        
    def _prepare_conversion_features(self, historical_data: List[Dict]) -> Tuple[List[List[float]], List[float]]:
        """Prepare features for conversion prediction."""
        features = []
        targets = []
        
        for data in historical_data:
            feature_vector = [
                data.get('quality_score', 0),
                data.get('response_time', 0),
                data.get('cost_usd', 0),
                data.get('user_satisfaction', 0),
                data.get('click_through_rate', 0),
                data.get('engagement_score', 0),
                data.get('relevance_score', 0),
            ]
            features.append(feature_vector)
            targets.append(data.get('conversion_rate', 0))
            
        return features, targets
        
    def _extract_prompt_features(self, prompt_features: Dict[str, Any]) -> List[float]:
        """Extract features from prompt data."""
        return [
            prompt_features.get('prompt_length', 0),
            prompt_features.get('word_count', 0),
            prompt_features.get('sentence_count', 0),
            prompt_features.get('avg_word_length', 0),
            prompt_features.get('complexity_score', 0),
            prompt_features.get('specificity_score', 0),
            prompt_features.get('clarity_score', 0),
            prompt_features.get('tone_score', 0),
            prompt_features.get('context_relevance', 0),
        ]
        
    def _extract_variant_features(self, variant: Dict) -> List[float]:
        """Extract features from variant data."""
        return [
            variant.get('quality_score', 0),
            variant.get('response_time', 0),
            variant.get('cost_usd', 0),
            variant.get('user_satisfaction', 0),
            variant.get('click_through_rate', 0),
            variant.get('engagement_score', 0),
            variant.get('relevance_score', 0),
        ]
        
    def _train_quality_model(self, X: List[List[float]], y: List[float]):
        """Train quality prediction model."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Store model and scaler
        self.models['quality'] = model
        self.scalers['quality'] = scaler
        
        return model
        
    def _train_cost_model(self, X: np.ndarray, y: np.ndarray):
        """Train cost prediction model."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Store model and scaler
        self.models['cost'] = model
        self.scalers['cost'] = scaler
        
        return model
        
    def _train_conversion_model(self, X: List[List[float]], y: List[float]):
        """Train conversion prediction model."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Store model and scaler
        self.models['conversion'] = model
        self.scalers['conversion'] = scaler
        
        return model
        
    def _calculate_confidence_interval(self, model, X: List[List[float]], y: List[float], 
                                     input_features: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for prediction."""
        # Simple approach: use model's prediction variance
        predictions = []
        
        # Bootstrap approach
        for _ in range(100):
            indices = np.random.choice(len(X), len(X), replace=True)
            X_bootstrap = [X[i] for i in indices]
            y_bootstrap = [y[i] for i in indices]
            
            # Train a simple model on bootstrap sample
            bootstrap_model = LinearRegression()
            bootstrap_model.fit(X_bootstrap, y_bootstrap)
            
            # Make prediction
            pred = bootstrap_model.predict([input_features])[0]
            predictions.append(pred)
            
        # Calculate confidence interval
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(predictions, lower_percentile)
        upper_bound = np.percentile(predictions, upper_percentile)
        
        return (lower_bound, upper_bound)
        
    def _calculate_model_accuracy(self, model, X: List[List[float]], y: List[float]) -> float:
        """Calculate model accuracy."""
        y_pred = model.predict(X)
        return r2_score(y, y_pred)
        
    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance from model."""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        else:
            importance = [1.0 / len(feature_names)] * len(feature_names)
            
        return dict(zip(feature_names, importance))
        
    def _default_prediction(self) -> PredictionResult:
        """Return default prediction when insufficient data."""
        return PredictionResult(
            predicted_value=0.5,
            confidence_interval=(0.3, 0.7),
            confidence_level=0.5,
            model_accuracy=0.0,
            features_importance={},
            prediction_horizon="default"
        ) 