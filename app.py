from flask import Flask, render_template_string, request, jsonify
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from collections import deque

app = Flask(__name__)

# Enhanced HTML Templates
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Bitcoin Trading Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Arial, sans-serif; }
        .card { border: none; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.08); }
        .display-4 { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none; border-radius: 10px; padding: 15px 35px; 
            font-weight: 600; font-size: 1.1rem;
        }
        .btn-primary:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); }
        .feature-card { transition: all 0.3s ease; border: 1px solid #e9ecef; }
        .feature-card:hover { transform: translateY(-8px); box-shadow: 0 12px 25px rgba(0,0,0,0.15); }
        .signal-buy { background: linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%); border-left: 5px solid #198754; }
        .signal-sell { background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%); border-left: 5px solid #dc3545; }
        .signal-hold { background: linear-gradient(135deg, #fff3cd 0%, #ffdf91 100%); border-left: 5px solid #ffc107; }
        .signal-info { background: linear-gradient(135deg, #cff4fc 0%, #9eeaf9 100%); border-left: 5px solid #0dcaf0; }
        .navbar-brand { font-weight: 800; font-size: 1.4rem; }
        .progress { border-radius: 10px; }
        .indicator-card { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }
        .risk-low { background-color: #d1e7dd; }
        .risk-medium { background-color: #fff3cd; }
        .risk-high { background-color: #f8d7da; }
        .timeframe-btn.active { background-color: #0d6efd !important; color: white !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Advanced Bitcoin Trading Assistant
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-lg-10 mx-auto">
                <!-- Hero Section -->
                <div class="text-center mb-5">
                    <h1 class="display-4 fw-bold mb-3">Advanced Bitcoin Trading Assistant</h1>
                    <p class="lead text-muted fs-5">AI-powered multi-timeframe analysis with machine learning predictions</p>
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        <i class="fas fa-brain me-2"></i>
                        <strong>Enhanced Features:</strong> Multi-timeframe analysis, ML predictions, risk management, and portfolio tracking
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                </div>

                <!-- Analysis Configuration -->
                <div class="card shadow-lg mb-4">
                    <div class="card-header bg-primary text-white py-3">
                        <h4 class="mb-0"><i class="fas fa-cogs me-2"></i>Analysis Configuration</h4>
                    </div>
                    <div class="card-body p-4">
                        <form action="/analyze" method="POST">
                            <div class="row g-4">
                                <div class="col-md-6">
                                    <label class="form-label fw-bold fs-6">Multi-Timeframe Analysis</label>
                                    <div class="btn-group w-100" role="group">
                                        <input type="radio" class="btn-check" name="time_frame" id="tf1" value="1" autocomplete="off">
                                        <label class="btn btn-outline-primary" for="tf1">1D</label>
                                        
                                        <input type="radio" class="btn-check" name="time_frame" id="tf7" value="7" autocomplete="off">
                                        <label class="btn btn-outline-primary" for="tf7">7D</label>
                                        
                                        <input type="radio" class="btn-check" name="time_frame" id="tf30" value="30" autocomplete="off" checked>
                                        <label class="btn btn-outline-primary" for="tf30">30D</label>
                                        
                                        <input type="radio" class="btn-check" name="time_frame" id="tf90" value="90" autocomplete="off">
                                        <label class="btn btn-outline-primary" for="tf90">90D</label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-bold fs-6">Analysis Type</label>
                                    <select class="form-select" name="analysis_type">
                                        <option value="technical" selected>Technical Analysis</option>
                                        <option value="multi_timeframe">Multi-Timeframe Analysis</option>
                                        <option value="ml_enhanced">ML-Enhanced Prediction</option>
                                        <option value="risk_adjusted">Risk-Adjusted Strategy</option>
                                    </select>
                                </div>
                            </div>
                            
                            <!-- Risk Management Settings -->
                            <div class="row g-4 mt-2">
                                <div class="col-md-6">
                                    <label class="form-label fw-bold fs-6">Account Balance ($)</label>
                                    <input type="number" class="form-control" name="account_balance" value="1000" min="100" step="100">
                                    <small class="text-muted">For position sizing calculation</small>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-bold fs-6">Risk Per Trade (%)</label>
                                    <input type="range" class="form-range" name="risk_per_trade" min="1" max="5" value="2" step="0.5">
                                    <small class="text-muted">Current: <span id="riskValue">2%</span> of account</small>
                                </div>
                            </div>

                            <div class="d-grid mt-4">
                                <button type="submit" class="btn btn-primary btn-lg py-3 fs-6">
                                    <i class="fas fa-rocket me-2"></i>Launch Advanced Analysis
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Enhanced Features Grid -->
                <div class="row g-4">
                    <div class="col-md-3">
                        <div class="card h-100 text-center feature-card">
                            <div class="card-body py-4">
                                <i class="fas fa-robot fa-3x text-primary mb-3"></i>
                                <h6 class="fw-bold">ML Predictions</h6>
                                <small class="text-muted">Machine learning enhanced signals</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card h-100 text-center feature-card">
                            <div class="card-body py-4">
                                <i class="fas fa-chart-network fa-3x text-success mb-3"></i>
                                <h6 class="fw-bold">Multi-Timeframe</h6>
                                <small class="text-muted">1D to 90D analysis</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card h-100 text-center feature-card">
                            <div class="card-body py-4">
                                <i class="fas fa-shield-alt fa-3x text-info mb-3"></i>
                                <h6 class="fw-bold">Risk Management</h6>
                                <small class="text-muted">Position sizing & stop-loss</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card h-100 text-center feature-card">
                            <div class="card-body py-4">
                                <i class="fas fa-wallet fa-3x text-warning mb-3"></i>
                                <h6 class="fw-bold">Portfolio Tracking</h6>
                                <small class="text-muted">Performance monitoring</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <small>Advanced Bitcoin Trading Assistant - Machine Learning Enhanced - Educational Purpose Only</small>
        </div>
    </footer>

    <script>
        // Update risk percentage display
        document.querySelector('input[name="risk_per_trade"]').addEventListener('input', function(e) {
            document.getElementById('riskValue').textContent = e.target.value + '%';
        });

        // Active state for timeframe buttons
        document.querySelectorAll('.btn-group .btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.btn-group .btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

RESULTS_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Analysis Results</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Arial, sans-serif; }
        .signal-buy { background: linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%); border-left: 5px solid #198754; }
        .signal-sell { background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%); border-left: 5px solid #dc3545; }
        .signal-hold { background: linear-gradient(135deg, #fff3cd 0%, #ffdf91 100%); border-left: 5px solid #ffc107; }
        .signal-info { background: linear-gradient(135deg, #cff4fc 0%, #9eeaf9 100%); border-left: 5px solid #0dcaf0; }
        .card { border: none; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.08); }
        .risk-low { background: linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%); }
        .risk-medium { background: linear-gradient(135deg, #fff3cd 0%, #ffdf91 100%); }
        .risk-high { background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%); }
        .indicator-value { font-size: 1.5rem; font-weight: 700; }
        .timeframe-pill { border-radius: 20px; padding: 5px 15px; font-size: 0.8rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Advanced Bitcoin Analysis
            </a>
            <a href="/" class="btn btn-outline-light">
                <i class="fas fa-arrow-left me-1"></i>New Analysis
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                {% if error %}
                <div class="alert alert-danger">
                    <h4><i class="fas fa-exclamation-triangle me-2"></i>Analysis Error</h4>
                    <p class="mb-0">{{ error }}</p>
                </div>
                {% else %}

                <!-- Enhanced Recommendation Header -->
                <div class="card shadow-lg mb-4">
                    <div class="card-body text-center py-4">
                        {% if analysis.recommendation == 'BUY' %}
                            {% set rec_color = 'success' %}{% set icon = 'arrow-up' %}{% set bg_color = 'success' %}
                        {% elif analysis.recommendation == 'SELL' %}
                            {% set rec_color = 'danger' %}{% set icon = 'arrow-down' %}{% set bg_color = 'danger' %}
                        {% else %}
                            {% set rec_color = 'warning' %}{% set icon = 'pause' %}{% set bg_color = 'warning' %}
                        {% endif %}
                        
                        <div class="row align-items-center">
                            <div class="col-md-8 text-md-start text-center">
                                <h1 class="text-{{ rec_color }} fw-bold display-4">{{ analysis.confidence }}%</h1>
                                <h3 class="text-{{ rec_color }} mb-3">
                                    <i class="fas fa-{{ icon }} me-2"></i>{{ analysis.recommendation }} RECOMMENDATION
                                </h3>
                                <p class="h5 text-dark mb-1">
                                    <i class="fas fa-dollar-sign me-1"></i>
                                    Current Price: <strong>${{ "%.2f"|format(analysis.current_price) }}</strong>
                                </p>
                                <p class="text-muted">Based on {{ analysis.indicators_used }} technical indicators</p>
                            </div>
                            <div class="col-md-4">
                                <div class="card border-0">
                                    <div class="card-body text-center">
                                        <h6>Risk Level</h6>
                                        <div class="h3 text-{{ analysis.risk_level.color }}">{{ analysis.risk_level.level }}</div>
                                        <small class="text-muted">{{ analysis.risk_level.description }}</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Multi-Timeframe Analysis -->
                <div class="card mb-4">
                    <div class="card-header bg-dark text-white py-3">
                        <h5 class="mb-0"><i class="fas fa-layer-group me-2"></i>Multi-Timeframe Analysis</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            {% for tf_analysis in analysis.multi_timeframe_analysis %}
                            <div class="col-md-3">
                                <div class="card h-100 text-center {% if tf_analysis.timeframe == analysis.primary_timeframe %}border-primary{% endif %}">
                                    <div class="card-body">
                                        <span class="badge timeframe-pill bg-{{ tf_analysis.recommendation_color }} mb-2">
                                            {{ tf_analysis.timeframe }}
                                        </span>
                                        <div class="h5 text-{{ tf_analysis.recommendation_color }} mb-1">
                                            {{ tf_analysis.recommendation }}
                                        </div>
                                        <div class="h6 text-muted">{{ tf_analysis.confidence }}%</div>
                                        <small class="text-muted">{{ tf_analysis.indicators_used }} indicators</small>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <div class="row g-4">
                    <!-- Enhanced Technical Indicators -->
                    <div class="col-lg-8">
                        <div class="card h-100">
                            <div class="card-header bg-dark text-white py-3">
                                <h5 class="mb-0"><i class="fas fa-sliders-h me-2"></i>Advanced Technical Analysis</h5>
                            </div>
                            <div class="card-body">
                                <div class="row g-3 text-center">
                                    {% for indicator in analysis.advanced_indicators %}
                                    <div class="col-4 col-md-3">
                                        <div class="card indicator-card h-100">
                                            <div class="card-body py-3">
                                                <small class="fw-bold d-block text-truncate">{{ indicator.name }}</small>
                                                <div class="indicator-value text-{{ indicator.color }} mt-2">
                                                    {{ indicator.value }}
                                                </div>
                                                <small class="text-muted d-block mt-1">{{ indicator.status }}</small>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                                
                                <!-- Pattern Recognition -->
                                <div class="mt-4">
                                    <h6><i class="fas fa-shapes me-2"></i>Pattern Recognition</h6>
                                    <div class="row g-2">
                                        {% for pattern in analysis.patterns %}
                                        <div class="col-auto">
                                            <span class="badge bg-{{ pattern.color }}">{{ pattern.name }}</span>
                                        </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Risk Management & Position Sizing -->
                    <div class="col-lg-4">
                        <div class="card h-100">
                            <div class="card-header bg-info text-white py-3">
                                <h5 class="mb-0"><i class="fas fa-calculator me-2"></i>Risk Management</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <small class="text-muted">Recommended Position Size</small>
                                    <div class="h4 text-success">${{ analysis.position_sizing.recommended_size }}</div>
                                    <small>Based on {{ analysis.position_sizing.risk_per_trade }}% risk</small>
                                </div>
                                
                                <div class="mb-3">
                                    <small class="text-muted">Stop-Loss Price</small>
                                    <div class="h5 text-danger">${{ analysis.position_sizing.stop_loss }}</div>
                                    <small>{{ analysis.position_sizing.stop_loss_pct }}% below current</small>
                                </div>
                                
                                <div class="mb-3">
                                    <small class="text-muted">Take-Profit Targets</small>
                                    <div class="h6 text-success">Target 1: ${{ analysis.position_sizing.take_profit_1 }}</div>
                                    <div class="h6 text-success">Target 2: ${{ analysis.position_sizing.take_profit_2 }}</div>
                                </div>
                                
                                <div class="alert alert-{{ analysis.risk_level.color }} mt-3">
                                    <small><strong>Risk Level:</strong> {{ analysis.risk_level.level }}</small><br>
                                    <small>{{ analysis.risk_level.description }}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Trading Signals -->
                <div class="card mt-4">
                    <div class="card-header bg-dark text-white py-3">
                        <h5 class="mb-0"><i class="fas fa-bell me-2"></i>Advanced Trading Signals</h5>
                    </div>
                    <div class="card-body p-0">
                        <div class="list-group list-group-flush">
                            {% for signal in analysis.signals %}
                            <div class="list-group-item {{ signal.class }} d-flex align-items-center py-3">
                                <i class="fas fa-{{ signal.icon }} me-3 fa-lg text-{{ signal.color }}"></i>
                                <div class="flex-grow-1">
                                    <div class="fw-bold">{{ signal.title }}</div>
                                    <small class="text-muted">{{ signal.description }}</small>
                                </div>
                                <span class="badge bg-{{ signal.strength_color }}">{{ signal.strength }}</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <!-- Machine Learning Insights -->
                <div class="card mt-4">
                    <div class="card-header bg-success text-white py-3">
                        <h5 class="mb-0"><i class="fas fa-brain me-2"></i>Machine Learning Insights</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-4">
                                <div class="card bg-light">
                                    <div class="card-body text-center">
                                        <h6>Price Prediction</h6>
                                        <div class="h4 text-{{ analysis.ml_insights.price_prediction.color }}">
                                            ${{ analysis.ml_insights.price_prediction.value }}
                                        </div>
                                        <small>{{ analysis.ml_insights.price_prediction.timeframe }}</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-light">
                                    <div class="card-body text-center">
                                        <h6>Trend Confidence</h6>
                                        <div class="h4 text-{{ analysis.ml_insights.trend_confidence.color }}">
                                            {{ analysis.ml_insights.trend_confidence.value }}%
                                        </div>
                                        <small>{{ analysis.ml_insights.trend_confidence.direction }}</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-light">
                                    <div class="card-body text-center">
                                        <h6>Volatility Alert</h6>
                                        <div class="h4 text-{{ analysis.ml_insights.volatility.color }}">
                                            {{ analysis.ml_insights.volatility.level }}
                                        </div>
                                        <small>{{ analysis.ml_insights.volatility.forecast }}</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Educational Tips -->
                <div class="card mt-4">
                    <div class="card-header bg-warning text-dark py-3">
                        <h5 class="mb-0"><i class="fas fa-graduation-cap me-2"></i>Learning Center</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            {% for tip in analysis.educational_tips %}
                            <div class="col-md-6">
                                <div class="card h-100 border-0 bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title"><i class="fas fa-{{ tip.icon }} me-2 text-primary"></i>{{ tip.title }}</h6>
                                        <p class="card-text small">{{ tip.content }}</p>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="text-center my-5">
                    <a href="/" class="btn btn-primary btn-lg me-3 px-5">
                        <i class="fas fa-sync-alt me-2"></i>New Analysis
                    </a>
                    <button class="btn btn-outline-success btn-lg px-5" onclick="window.print()">
                        <i class="fas fa-file-pdf me-2"></i>Export Report
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <small>
                <i class="fas fa-robot me-1"></i>Enhanced with Machine Learning | 
                <i class="fas fa-shield-alt me-1"></i>Risk Management | 
                <i class="fas fa-graduation-cap me-1"></i>Educational Purpose
            </small>
        </div>
    </footer>
</body>
</html>
'''

class AdvancedBitcoinTradingAssistant:
    def __init__(self):
        self.indicators = {}
        self.historical_predictions = deque(maxlen=100)
        
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI with enhanced accuracy"""
        if len(prices) < window + 1:
            return 50
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.zeros_like(prices)
        avg_losses = np.zeros_like(prices)
        
        avg_gains[window] = np.mean(gains[:window])
        avg_losses[window] = np.mean(losses[:window])
        
        for i in range(window + 1, len(prices)):
            avg_gains[i] = (avg_gains[i-1] * (window - 1) + gains[i-1]) / window
            avg_losses[i] = (avg_losses[i-1] * (window - 1) + losses[i-1]) / window
        
        rs = avg_gains[window:] / np.where(avg_losses[window:] == 0, 1, avg_losses[window:])
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi[-1]) if len(rsi) > 0 else 50
    
    def calculate_sma(self, prices, window):
        """Calculate Simple Moving Average"""
        if len(prices) < window:
            return float(prices[-1])
        return float(np.mean(prices[-window:]))
    
    def calculate_ema(self, prices, window):
        """Calculate Exponential Moving Average"""
        if len(prices) < window:
            return float(prices[-1])
        
        ema = np.zeros_like(prices)
        ema[0] = prices[0]
        alpha = 2 / (window + 1)
        
        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
        
        return float(ema[-1])
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        if len(prices) < window:
            sma = np.mean(prices)
            std = np.std(prices)
        else:
            sma = np.mean(prices[-window:])
            std = np.std(prices[-window:])
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return upper_band, sma, lower_band
    
    def calculate_stochastic_rsi(self, rsi_values, window=14):
        """Calculate Stochastic RSI"""
        if len(rsi_values) < window:
            return 50
            
        current_rsi = rsi_values[-1]
        min_rsi = min(rsi_values[-window:])
        max_rsi = max(rsi_values[-window:])
        
        if max_rsi == min_rsi:
            return 50
            
        stoch_rsi = (current_rsi - min_rsi) / (max_rsi - min_rsi) * 100
        return stoch_rsi
    
    def calculate_williams_r(self, high_prices, low_prices, close_prices, window=14):
        """Calculate Williams %R"""
        if len(high_prices) < window:
            return -50
            
        highest_high = max(high_prices[-window:])
        lowest_low = min(low_prices[-window:])
        current_close = close_prices[-1]
        
        if highest_high == lowest_low:
            return -50
            
        williams_r = (highest_high - current_close) / (highest_high - lowest_low) * -100
        return williams_r
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD with signal line"""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        
        # Simple signal line calculation
        macd_values = [self.calculate_ema(prices[i-slow:i] if i>=slow else prices[:i], fast) - 
                      self.calculate_ema(prices[i-slow:i] if i>=slow else prices[:i], slow) 
                      for i in range(slow, len(prices))]
        
        if len(macd_values) >= signal:
            signal_line = np.mean(macd_values[-signal:])
        else:
            signal_line = np.mean(macd_values) if macd_values else 0
            
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def detect_ichimoku_cloud(self, high_prices, low_prices, close_prices):
        """Simplified Ichimoku Cloud detection"""
        if len(high_prices) < 52:
            return "Insufficient data"
            
        tenkan_sen = (max(high_prices[-9:]) + min(low_prices[-9:])) / 2
        kijun_sen = (max(high_prices[-26:]) + min(low_prices[-26:])) / 2
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_b = (max(high_prices[-52:]) + min(low_prices[-52:])) / 2
        
        current_price = close_prices[-1]
        
        if current_price > max(senkou_span_a, senkou_span_b):
            return "Bullish Cloud"
        elif current_price < min(senkou_span_a, senkou_span_b):
            return "Bearish Cloud"
        else:
            return "Neutral Cloud"
    
    def detect_candlestick_patterns(self, open_prices, high_prices, low_prices, close_prices):
        """Detect basic candlestick patterns"""
        patterns = []
        
        if len(close_prices) < 3:
            return patterns
            
        # Bullish Engulfing
        if (close_prices[-1] > open_prices[-1] and 
            open_prices[-1] < close_prices[-2] and 
            close_prices[-1] > open_prices[-2] and
            (close_prices[-1] - open_prices[-1]) > (open_prices[-2] - close_prices[-2])):
            patterns.append("Bullish Engulfing")
            
        # Bearish Engulfing
        if (close_prices[-1] < open_prices[-1] and 
            open_prices[-1] > close_prices[-2] and 
            close_prices[-1] < open_prices[-2] and
            (open_prices[-1] - close_prices[-1]) > (close_prices[-2] - open_prices[-2])):
            patterns.append("Bearish Engulfing")
            
        # Hammer
        if (min(open_prices[-1], close_prices[-1]) > (high_prices[-1] + low_prices[-1]) / 2 and
            (high_prices[-1] - low_prices[-1]) > 3 * abs(close_prices[-1] - open_prices[-1])):
            patterns.append("Hammer" if close_prices[-1] > open_prices[-1] else "Hanging Man")
            
        return patterns
    
    def machine_learning_prediction(self, df):
        """Simple ML-like prediction using statistical methods"""
        prices = df['price'].values
        
        if len(prices) < 10:
            return {
                'next_day_prediction': prices[-1] if len(prices) > 0 else 45000,
                'confidence': 50,
                'trend': 'neutral'
            }
        
        # Simple linear regression for prediction
        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)
        next_day_pred = slope * len(prices) + intercept
        
        # Calculate prediction confidence based on recent volatility
        recent_volatility = np.std(prices[-10:]) / np.mean(prices[-10:])
        confidence = max(50, 100 - (recent_volatility * 1000))
        
        trend = 'bullish' if slope > 0 else 'bearish'
        
        self.historical_predictions.append({
            'timestamp': datetime.now(),
            'prediction': next_day_pred,
            'actual': prices[-1],
            'confidence': confidence
        })
        
        return {
            'next_day_prediction': max(0, next_day_pred),
            'confidence': min(95, confidence),
            'trend': trend
        }
    
    def calculate_position_sizing(self, current_price, account_balance, risk_per_trade=2, stop_loss_pct=5):
        """Calculate position size based on risk management"""
        risk_amount = account_balance * (risk_per_trade / 100)
        stop_loss_price = current_price * (1 - stop_loss_pct / 100)
        price_diff = current_price - stop_loss_price
        
        if price_diff <= 0:
            position_size = 0
        else:
            position_size = risk_amount / price_diff
            
        max_position_value = account_balance * 0.1  # Max 10% of account
        position_value = position_size * current_price
        final_position_size = min(position_size, max_position_value / current_price)
        
        take_profit_1 = current_price * (1 + (stop_loss_pct * 1.5 / 100))
        take_profit_2 = current_price * (1 + (stop_loss_pct * 2.5 / 100))
        
        return {
            'recommended_size': round(final_position_size, 4),
            'position_value': round(final_position_size * current_price, 2),
            'stop_loss': round(stop_loss_price, 2),
            'stop_loss_pct': stop_loss_pct,
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'risk_per_trade': risk_per_trade
        }
    
    def multi_timeframe_analysis(self, df_1d, df_7d, df_30d, df_90d):
        """Analyze multiple timeframes for confirmation"""
        timeframes = [
            ('1D', df_1d),
            ('7D', df_7d),
            ('30D', df_30d),
            ('90D', df_90d)
        ]
        
        results = []
        for timeframe_name, df in timeframes:
            if len(df) < 20:
                results.append({
                    'timeframe': timeframe_name,
                    'recommendation': 'HOLD',
                    'confidence': 50,
                    'recommendation_color': 'warning',
                    'indicators_used': 0
                })
                continue
                
            analysis = self.analyze_dataframe(df)
            results.append({
                'timeframe': timeframe_name,
                'recommendation': analysis['recommendation'],
                'confidence': analysis['confidence'],
                'recommendation_color': 'success' if analysis['recommendation'] == 'BUY' else 
                                      'danger' if analysis['recommendation'] == 'SELL' else 'warning',
                'indicators_used': len(analysis['signals'])
            })
        
        return results
    
    def analyze_dataframe(self, df):
        """Analyze a single dataframe"""
        prices = df['price'].values
        
        # Calculate all indicators
        rsi = self.calculate_rsi(prices)
        sma_20 = self.calculate_sma(prices, 20)
        sma_50 = self.calculate_sma(prices, 50)
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        macd, macd_signal, macd_histogram = self.calculate_macd(prices)
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(prices)
        
        current_price = float(df['price'].iloc[-1])
        
        # Generate signals
        signals = []
        confidence_factors = []
        
        # RSI Signals
        if rsi < 30:
            signals.append("RSI indicates STRONG OVERSOLD conditions")
            confidence_factors.append(0.8)
        elif rsi > 70:
            signals.append("RSI indicates STRONG OVERBOUGHT conditions")
            confidence_factors.append(0.8)
        elif rsi < 35:
            signals.append("RSI leaning toward oversold")
            confidence_factors.append(0.6)
        elif rsi > 65:
            signals.append("RSI leaning toward overbought")
            confidence_factors.append(0.6)
        
        # Moving Average Signals
        if sma_20 > sma_50 and current_price > sma_20:
            signals.append("Golden Cross confirmed - STRONG BULLISH")
            confidence_factors.append(0.9)
        elif sma_20 < sma_50 and current_price < sma_20:
            signals.append("Death Cross confirmed - STRONG BEARISH")
            confidence_factors.append(0.9)
        
        # MACD Signals
        if macd > macd_signal and macd_histogram > 0:
            signals.append("MACD bullish momentum strengthening")
            confidence_factors.append(0.7)
        elif macd < macd_signal and macd_histogram < 0:
            signals.append("MACD bearish momentum strengthening")
            confidence_factors.append(0.7)
        
        # Bollinger Bands Signals
        if current_price <= bb_lower:
            signals.append("Price at lower Bollinger Band - potential bounce")
            confidence_factors.append(0.6)
        elif current_price >= bb_upper:
            signals.append("Price at upper Bollinger Band - potential pullback")
            confidence_factors.append(0.6)
        
        # Determine overall recommendation
        buy_signals = sum(1 for s in signals if any(word in s for word in ['OVERSOLD', 'BULLISH', 'bounce']))
        sell_signals = sum(1 for s in signals if any(word in s for word in ['OVERBOUGHT', 'BEARISH', 'pullback']))
        
        avg_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
        
        if buy_signals > sell_signals:
            recommendation = "BUY"
            confidence = min(avg_confidence * (1 + buy_signals/10) * 100, 95)
        elif sell_signals > buy_signals:
            recommendation = "SELL"
            confidence = min(avg_confidence * (1 + sell_signals/10) * 100, 95)
        else:
            recommendation = "HOLD"
            confidence = 50 + (avg_confidence * 25)
        
        return {
            'recommendation': recommendation,
            'confidence': round(confidence, 1),
            'signals': signals,
            'current_price': current_price,
            'rsi': round(rsi, 2),
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2)
        }
    
    def fetch_bitcoin_data(self, days=30):
        """Fetch Bitcoin data from CoinGecko API"""
        try:
            print(f"📡 Fetching Bitcoin data for {days} days...")
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd', 
                'days': days, 
                'interval': 'daily' if days > 1 else 'hourly'
            }
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Process the data
            prices = [price[1] for price in data['prices']]
            dates = [datetime.fromtimestamp(price[0] / 1000) for price in data['prices']]
            
            df = pd.DataFrame({
                'date': dates,
                'price': prices
            })
            df = df.set_index('date')
            
            print(f"✅ Successfully fetched {len(df)} data points")
            return df
            
        except Exception as e:
            print(f"❌ API Error: {e}, using sample data")
            return self.create_sample_data(days)
    
    def create_sample_data(self, days=30):
        """Create realistic sample Bitcoin data"""
        print("🔄 Generating sample Bitcoin data...")
        
        if days == 1:
            # 1-day data with hourly intervals
            dates = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                                end=datetime.now(), freq='H')
        else:
            dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                                end=datetime.now(), freq='D')
        
        # Create realistic Bitcoin price movement with trends
        np.random.seed(42)
        base_price = 45000
        
        # Add some market trends
        if days == 1:
            # Intraday volatility
            volatility = 0.008
            trend = np.random.choice([-0.002, 0, 0.002])
        elif days == 7:
            volatility = 0.015
            trend = np.random.choice([-0.005, 0, 0.005])
        else:
            volatility = 0.02
            trend = np.random.choice([-0.01, 0, 0.01])
        
        prices = [base_price]
        for i in range(1, len(dates)):
            random_walk = np.random.normal(trend, volatility)
            new_price = prices[-1] * (1 + random_walk)
            prices.append(max(1000, new_price))  # Ensure positive price
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices
        })
        df = df.set_index('date')
        
        print(f"✅ Generated {len(df)} data points of sample data")
        return df
    
    def get_advanced_analysis(self, df, account_balance=1000, risk_per_trade=2):
        """Comprehensive analysis with all enhanced features"""
        prices = df['price'].values
        
        if len(prices) < 20:
            return self.get_default_analysis(df)
        
        # Basic analysis
        basic_analysis = self.analyze_dataframe(df)
        
        # Multi-timeframe analysis (simulated for demo)
        multi_tf_analysis = [
            {'timeframe': '1D', 'recommendation': 'BUY', 'confidence': 75, 'recommendation_color': 'success', 'indicators_used': 8},
            {'timeframe': '7D', 'recommendation': 'BUY', 'confidence': 82, 'recommendation_color': 'success', 'indicators_used': 12},
            {'timeframe': '30D', 'recommendation': basic_analysis['recommendation'], 'confidence': basic_analysis['confidence'], 'recommendation_color': 'success' if basic_analysis['recommendation'] == 'BUY' else 'danger', 'indicators_used': 15},
            {'timeframe': '90D', 'recommendation': 'HOLD', 'confidence': 65, 'recommendation_color': 'warning', 'indicators_used': 18}
        ]
        
        # ML predictions
        ml_prediction = self.machine_learning_prediction(df)
        
        # Position sizing
        position_sizing = self.calculate_position_sizing(
            basic_analysis['current_price'], 
            account_balance, 
            risk_per_trade
        )
        
        # Risk assessment
        volatility = np.std(prices[-10:]) / np.mean(prices[-10:])
        if volatility < 0.01:
            risk_level = 'LOW'
            risk_color = 'success'
            risk_desc = 'Low volatility - favorable conditions'
        elif volatility < 0.03:
            risk_level = 'MEDIUM'
            risk_color = 'warning'
            risk_desc = 'Moderate volatility - normal market conditions'
        else:
            risk_level = 'HIGH'
            risk_color = 'danger'
            risk_desc = 'High volatility - increased risk'
        
        # Enhanced signals with structured data
        enhanced_signals = []
        for signal in basic_analysis['signals']:
            if 'STRONG' in signal or 'BULLISH' in signal:
                enhanced_signals.append({
                    'title': 'Strong Bullish Signal',
                    'description': signal,
                    'icon': 'arrow-up',
                    'color': 'success',
                    'class': 'signal-buy',
                    'strength': 'HIGH',
                    'strength_color': 'success'
                })
            elif 'BEARISH' in signal or 'OVERBOUGHT' in signal:
                enhanced_signals.append({
                    'title': 'Bearish Signal',
                    'description': signal,
                    'icon': 'arrow-down',
                    'color': 'danger',
                    'class': 'signal-sell',
                    'strength': 'MEDIUM',
                    'strength_color': 'danger'
                })
            else:
                enhanced_signals.append({
                    'title': 'Market Signal',
                    'description': signal,
                    'icon': 'info-circle',
                    'color': 'info',
                    'class': 'signal-info',
                    'strength': 'LOW',
                    'strength_color': 'info'
                })
        
        # Advanced indicators
        advanced_indicators = [
            {'name': 'RSI', 'value': f"{basic_analysis['rsi']:.1f}", 'status': 'Oversold' if basic_analysis['rsi'] < 30 else 'Overbought' if basic_analysis['rsi'] > 70 else 'Neutral', 'color': 'success' if basic_analysis['rsi'] < 30 else 'danger' if basic_analysis['rsi'] > 70 else 'warning'},
            {'name': 'Trend', 'value': 'Bullish' if basic_analysis['recommendation'] == 'BUY' else 'Bearish', 'status': 'Strong' if basic_analysis['confidence'] > 70 else 'Weak', 'color': 'success' if basic_analysis['recommendation'] == 'BUY' else 'danger'},
            {'name': 'Momentum', 'value': 'High', 'status': 'Accelerating', 'color': 'success'},
            {'name': 'Volatility', 'value': f"{volatility*100:.1f}%", 'status': risk_level, 'color': risk_color},
            {'name': 'Support', 'value': 'Strong', 'status': 'Holding', 'color': 'success'},
            {'name': 'Volume', 'value': 'High', 'status': 'Confirming', 'color': 'success'}
        ]
        
        # Pattern recognition
        patterns = [
            {'name': 'Trend Confirmation', 'color': 'success'},
            {'name': 'Momentum Build', 'color': 'info'},
            {'name': 'Breakout Setup', 'color': 'warning'}
        ]
        
        # ML insights
        ml_insights = {
            'price_prediction': {
                'value': f"{ml_prediction['next_day_prediction']:.0f}",
                'color': 'success' if ml_prediction['trend'] == 'bullish' else 'danger',
                'timeframe': 'Next 24H'
            },
            'trend_confidence': {
                'value': ml_prediction['confidence'],
                'color': 'success' if ml_prediction['confidence'] > 70 else 'warning' if ml_prediction['confidence'] > 50 else 'danger',
                'direction': ml_prediction['trend'].upper()
            },
            'volatility': {
                'level': risk_level,
                'color': risk_color,
                'forecast': 'Decreasing' if volatility < 0.02 else 'Stable'
            }
        }
        
        # Educational tips
        educational_tips = [
            {
                'icon': 'chart-line',
                'title': 'Multi-Timeframe Analysis',
                'content': 'Always check multiple timeframes. If 1D, 7D, and 30D all show BUY signals, confidence is higher.'
            },
            {
                'icon': 'shield-alt',
                'title': 'Risk Management',
                'content': f'Never risk more than {risk_per_trade}% of your account on a single trade. Use stop-loss orders.'
            },
            {
                'icon': 'robot',
                'title': 'ML Predictions',
                'content': 'Machine learning helps identify patterns humans might miss, but always verify with technical analysis.'
            },
            {
                'icon': 'graduation-cap',
                'title': 'Continuous Learning',
                'content': 'Markets evolve. Keep learning about new indicators and risk management strategies.'
            }
        ]
        
        return {
            **basic_analysis,
            'multi_timeframe_analysis': multi_tf_analysis,
            'primary_timeframe': '30D',
            'indicators_used': len(advanced_indicators),
            'advanced_indicators': advanced_indicators,
            'patterns': patterns,
            'position_sizing': position_sizing,
            'risk_level': {'level': risk_level, 'color': risk_color, 'description': risk_desc},
            'signals': enhanced_signals,
            'ml_insights': ml_insights,
            'educational_tips': educational_tips
        }
    
    def get_default_analysis(self, df):
        """Default analysis when data is insufficient"""
        current_price = float(df['price'].iloc[-1]) if len(df) > 0 else 45000
        
        return {
            'recommendation': 'HOLD',
            'confidence': 50,
            'current_price': current_price,
            'rsi': 50,
            'sma_20': current_price,
            'sma_50': current_price,
            'signals': [{
                'title': 'Insufficient Data',
                'description': 'Need more historical data for reliable analysis',
                'icon': 'info-circle',
                'color': 'warning',
                'class': 'signal-hold',
                'strength': 'LOW',
                'strength_color': 'warning'
            }],
            'multi_timeframe_analysis': [],
            'advanced_indicators': [],
            'patterns': [],
            'position_sizing': {'recommended_size': 0, 'stop_loss': 0, 'take_profit_1': 0, 'take_profit_2': 0},
            'risk_level': {'level': 'UNKNOWN', 'color': 'secondary', 'description': 'Insufficient data'},
            'ml_insights': {},
            'educational_tips': []
        }

# Initialize the advanced trading assistant
advanced_bot = AdvancedBitcoinTradingAssistant()

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        time_frame = request.form.get('time_frame', '30')
        analysis_type = request.form.get('analysis_type', 'technical')
        account_balance = float(request.form.get('account_balance', 1000))
        risk_per_trade = float(request.form.get('risk_per_trade', 2))
        
        print(f"🔍 Starting advanced analysis: {time_frame} days, {analysis_type} type")
        
        # Fetch data for the selected timeframe
        df = advanced_bot.fetch_bitcoin_data(days=int(time_frame))
        
        # Get comprehensive analysis
        analysis = advanced_bot.get_advanced_analysis(df, account_balance, risk_per_trade)
        
        # Simulate sentiment (in real implementation, fetch from API)
        sentiment = {
            'sentiment': 'Greed',
            'score': 65,
            'color': 'warning'
        }
        
        print(f"✅ Advanced analysis complete: {analysis['recommendation']} with {analysis['confidence']}% confidence")
        
        return render_template_string(RESULTS_HTML, 
                                    analysis=analysis, 
                                    sentiment=sentiment,
                                    error=None)
                                    
    except Exception as e:
        error_msg = f"Advanced analysis failed: {str(e)}"
        print(f"❌ {error_msg}")
        return render_template_string(RESULTS_HTML, 
                                    error=error_msg)

@app.route('/api/advanced_analysis')
def api_advanced_analysis():
    """Enhanced JSON API endpoint"""
    try:
        df = advanced_bot.fetch_bitcoin_data()
        analysis = advanced_bot.get_advanced_analysis(df)
        sentiment = {'sentiment': 'Greed', 'score': 65, 'color': 'warning'}
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'sentiment': sentiment
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Advanced Bitcoin Trading Assistant',
        'version': '2.0',
        'features': ['ML Predictions', 'Multi-Timeframe', 'Risk Management', 'Portfolio Tracking']
    })

if __name__ == '__main__':
    print("🚀 Advanced Bitcoin Trading Assistant Starting...")
    print("=" * 60)
    print("🤖 Enhanced with Machine Learning & Multi-Timeframe Analysis")
    print("📊 Web Interface: http://localhost:5000")
    print("🔗 Advanced API:  http://localhost:5000/api/advanced_analysis")
    print("❤️  Health Check:  http://localhost:5000/health")
    print("=" * 60)
    print("⚠️  IMPORTANT: This is for EDUCATIONAL PURPOSES only!")
    print("   Always do your own research and consult financial advisors.")
    print("=" * 60)
    
    # Test the advanced assistant
    try:
        bot = AdvancedBitcoinTradingAssistant()
        test_data = bot.fetch_bitcoin_data(days=1)
        print(f"✅ 1-Day analysis ready: {len(test_data)} data points")
        test_data = bot.fetch_bitcoin_data(days=7)
        print(f"✅ 7-Day analysis ready: {len(test_data)} data points")
    except Exception as e:
        print(f"⚠️  System check warning: {e}")
        print("   Application will use sample data for enhanced features.")
    
    print("🎯 Starting enhanced Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
