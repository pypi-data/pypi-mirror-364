"""
Ensemble Models Module for MeridianAlgo
Provides ensemble machine learning models for enhanced prediction accuracy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

try:
    import torch
    import torch.nn as nn
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TORCH_AVAILABLE = False


class EnsembleModels:
    """
    Ensemble machine learning models for stock prediction
    """
    
    def __init__(self, device: str = "auto"):
        """
        Initialize ensemble models
        
        Args:
            device: Device for computation ("auto", "cpu", "cuda", "mps")
        """
        self.device = self._get_device(device) if TORCH_AVAILABLE else "cpu"
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        
    def _get_device(self, device: str) -> str:
        """Get the best available device"""
        if not TORCH_AVAILABLE:
            return "cpu"
            
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def prepare_ensemble_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for ensemble training
        
        Args:
            data: DataFrame with OHLCV and technical indicators
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Features and targets
        """
        # Enhanced feature set
        feature_columns = [
            'Open', 'High', 'Low', 'Close', 'Volume'
        ]
        
        # Add technical indicators if available
        technical_indicators = [
            'SMA_10', 'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
            'RSI', 'MACD', 'MACD_Signal', 'BB_Position',
            'Volume_Ratio', 'Price_Change', 'Price_Momentum'
        ]
        
        available_features = [col for col in feature_columns + technical_indicators 
                            if col in data.columns]
        
        X = data[available_features].values
        y = data['Close'].shift(-1).dropna().values  # Next day's close
        X = X[:-1]  # Match target length
        
        return X, y
    
    def train_ensemble(self, X: np.ndarray, y: np.ndarray, 
                      epochs: int = 10, verbose: bool = False) -> Dict:
        """
        Train ensemble of models
        
        Args:
            X: Feature matrix
            y: Target vector
            epochs: Training epochs for neural networks
            verbose: Print training progress
            
        Returns:
            Dict: Training results
        """
        try:
            results = {}
            
            # Split data for training and validation
            split_idx = int(0.8 * len(X))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Scale data
            self.scalers['features'] = MinMaxScaler()
            self.scalers['target'] = MinMaxScaler()
            
            X_train_scaled = self.scalers['features'].fit_transform(X_train)
            X_val_scaled = self.scalers['features'].transform(X_val)
            y_train_scaled = self.scalers['target'].fit_transform(y_train.reshape(-1, 1)).flatten()
            y_val_scaled = self.scalers['target'].transform(y_val.reshape(-1, 1)).flatten()
            
            # Train Linear Regression (always available)
            if verbose:
                print("Training Linear Regression...")
            self.models['linear'] = LinearRegression()
            self.models['linear'].fit(X_train_scaled, y_train_scaled)
            
            # Evaluate linear model
            linear_pred = self.models['linear'].predict(X_val_scaled)
            linear_mse = np.mean((linear_pred - y_val_scaled) ** 2)
            results['linear_mse'] = linear_mse
            
            # Train Random Forest (if sklearn available)
            if SKLEARN_AVAILABLE:
                if verbose:
                    print("Training Random Forest...")
                self.models['random_forest'] = RandomForestRegressor(
                    n_estimators=50, random_state=42, n_jobs=-1
                )
                self.models['random_forest'].fit(X_train_scaled, y_train_scaled)
                
                # Evaluate RF model
                rf_pred = self.models['random_forest'].predict(X_val_scaled)
                rf_mse = np.mean((rf_pred - y_val_scaled) ** 2)
                results['random_forest_mse'] = rf_mse
            
            # Train Neural Network (if torch available)
            if TORCH_AVAILABLE:
                if verbose:
                    print("Training Neural Network...")
                
                input_size = X_train_scaled.shape[1]
                self.models['neural_net'] = EnhancedNN(input_size).to(self.device)
                
                # Train neural network
                nn_mse = self._train_neural_network(
                    self.models['neural_net'], 
                    X_train_scaled, y_train_scaled,
                    X_val_scaled, y_val_scaled,
                    epochs, verbose
                )
                results['neural_net_mse'] = nn_mse
            
            self.is_trained = True
            results['training_samples'] = len(X_train)
            results['validation_samples'] = len(X_val)
            results['features'] = X.shape[1]
            
            if verbose:
                print(f"Ensemble training completed. Models trained: {list(self.models.keys())}")
            
            return results
            
        except Exception as e:
            raise ValueError(f"Ensemble training failed: {str(e)}")
    
    def _train_neural_network(self, model, X_train, y_train, X_val, y_val, 
                            epochs: int, verbose: bool) -> float:
        """Train neural network model"""
        X_train_tensor = torch.FloatTensor(X_train).to(self.device)
        y_train_tensor = torch.FloatTensor(y_train).to(self.device)
        X_val_tensor = torch.FloatTensor(X_val).to(self.device)
        y_val_tensor = torch.FloatTensor(y_val).to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = model(X_train_tensor)
            loss = criterion(outputs.squeeze(), y_train_tensor)
            loss.backward()
            optimizer.step()
            
            if verbose and (epoch + 1) % (epochs // 5) == 0:
                model.eval()
                with torch.no_grad():
                    val_outputs = model(X_val_tensor)
                    val_loss = criterion(val_outputs.squeeze(), y_val_tensor)
                    print(f"Epoch {epoch+1}/{epochs}, Train Loss: {loss.item():.6f}, Val Loss: {val_loss.item():.6f}")
                model.train()
        
        # Final validation loss
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_tensor)
            val_mse = criterion(val_outputs.squeeze(), y_val_tensor).item()
        
        return val_mse
    
    def predict_ensemble(self, X: np.ndarray, forecast_days: int = 5) -> Dict:
        """
        Make ensemble predictions
        
        Args:
            X: Feature matrix
            forecast_days: Number of days to forecast
            
        Returns:
            Dict: Ensemble predictions
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        try:
            # Scale input features
            X_scaled = self.scalers['features'].transform(X)
            last_features = X_scaled[-1:] if len(X_scaled.shape) > 1 else X_scaled.reshape(1, -1)
            
            predictions = {}
            ensemble_predictions = []
            
            # Get predictions from each model
            for model_name, model in self.models.items():
                if model_name == 'neural_net' and TORCH_AVAILABLE:
                    model_preds = self._predict_neural_network(model, last_features, forecast_days)
                else:
                    model_preds = self._predict_sklearn_model(model, last_features, forecast_days)
                
                # Inverse transform predictions
                model_preds_original = self.scalers['target'].inverse_transform(
                    model_preds.reshape(-1, 1)
                ).flatten()
                
                predictions[model_name] = model_preds_original.tolist()
            
            # Calculate ensemble prediction (weighted average)
            weights = self._calculate_model_weights()
            
            for i in range(forecast_days):
                ensemble_pred = 0
                total_weight = 0
                
                for model_name, weight in weights.items():
                    if model_name in predictions and i < len(predictions[model_name]):
                        ensemble_pred += predictions[model_name][i] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    ensemble_predictions.append(ensemble_pred / total_weight)
                else:
                    # Fallback to simple average
                    model_preds_at_i = [predictions[m][i] for m in predictions if i < len(predictions[m])]
                    ensemble_predictions.append(np.mean(model_preds_at_i) if model_preds_at_i else 0)
            
            # Calculate prediction confidence
            confidence = self._calculate_ensemble_confidence(predictions, ensemble_predictions)
            
            return {
                'ensemble_predictions': ensemble_predictions,
                'individual_predictions': predictions,
                'confidence': confidence,
                'models_used': list(self.models.keys()),
                'forecast_days': forecast_days
            }
            
        except Exception as e:
            raise ValueError(f"Ensemble prediction failed: {str(e)}")
    
    def _predict_neural_network(self, model, features, forecast_days: int) -> np.ndarray:
        """Make predictions using neural network"""
        model.eval()
        predictions = []
        
        current_features = torch.FloatTensor(features).to(self.device)
        
        with torch.no_grad():
            for _ in range(forecast_days):
                pred = model(current_features)
                predictions.append(pred.cpu().numpy()[0, 0])
                
                # Simple feature update (in practice, you'd want more sophisticated approach)
                # For now, just repeat the prediction
        
        return np.array(predictions)
    
    def _predict_sklearn_model(self, model, features, forecast_days: int) -> np.ndarray:
        """Make predictions using sklearn model"""
        predictions = []
        
        for _ in range(forecast_days):
            pred = model.predict(features)[0]
            predictions.append(pred)
            
            # Simple feature update
            # For now, just repeat the prediction
        
        return np.array(predictions)
    
    def _calculate_model_weights(self) -> Dict[str, float]:
        """Calculate weights for ensemble based on model performance"""
        # Simple equal weighting for now
        # In practice, you'd weight based on validation performance
        num_models = len(self.models)
        return {model_name: 1.0 / num_models for model_name in self.models.keys()}
    
    def _calculate_ensemble_confidence(self, individual_predictions: Dict, 
                                     ensemble_predictions: List[float]) -> float:
        """Calculate confidence in ensemble predictions"""
        try:
            if not individual_predictions or not ensemble_predictions:
                return 50.0
            
            # Calculate prediction variance across models
            variances = []
            for i in range(len(ensemble_predictions)):
                day_predictions = [individual_predictions[model][i] 
                                for model in individual_predictions 
                                if i < len(individual_predictions[model])]
                
                if len(day_predictions) > 1:
                    variance = np.var(day_predictions)
                    variances.append(variance)
            
            if not variances:
                return 75.0
            
            # Lower variance = higher confidence
            avg_variance = np.mean(variances)
            max_expected_variance = (ensemble_predictions[0] * 0.1) ** 2  # 10% of price
            
            confidence = max(50, 95 - (avg_variance / max_expected_variance) * 30)
            return min(confidence, 95)
            
        except Exception:
            return 70.0
    
    def get_model_info(self) -> Dict:
        """Get information about trained models"""
        return {
            'is_trained': self.is_trained,
            'available_models': list(self.models.keys()),
            'device': self.device,
            'sklearn_available': SKLEARN_AVAILABLE,
            'torch_available': TORCH_AVAILABLE
        }


class EnhancedNN(nn.Module):
    """Enhanced neural network for stock prediction"""
    
    def __init__(self, input_size: int):
        super(EnhancedNN, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(32, 16),
            nn.ReLU(),
            
            nn.Linear(16, 1)
        )
    
    def forward(self, x):
        return self.network(x)


class LSTMPredictor(nn.Module):
    """LSTM-based predictor for time series"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2):
        super(LSTMPredictor, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # x shape: (batch_size, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # Take the last output
        output = self.fc(lstm_out[:, -1, :])
        return output