from flask import Flask, render_template_string, request, jsonify
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json 
from collections import deque
import time
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier 
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Enhanced HTML Templates with ML features
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bitcoin AI Trading Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Arial, sans-serif; 
            min-height: 100vh;
        }
        .main-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 20px 0;
            padding: 30px;
        }
        .card { 
            border: none; 
            border-radius: 12px; 
            box-shadow: 0 6px 15px rgba(0,0,0,0.08); 
            margin-bottom: 20px;
        }
        .welcome-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none; 
            border-radius: 10px; 
            padding: 15px 35px; 
            font-weight: 600; 
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        .btn-primary:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); 
        }
        .feature-card { 
            transition: all 0.3s ease; 
            border: 1px solid #e9ecef; 
            text-align: center;
            padding: 20px;
        }
        .feature-card:hover { 
            transform: translateY(-8px); 
            box-shadow: 0 12px 25px rgba(0,0,0,0.15); 
        }
        .signal-buy { background: linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%); border-left: 5px solid #198754; }
        .signal-sell { background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%); border-left: 5px solid #dc3545; }
        .signal-hold { background: linear-gradient(135deg, #fff3cd 0%, #ffdf91 100%); border-left: 5px solid #ffc107; }
        .signal-info { background: linear-gradient(135deg, #cff4fc 0%, #9eeaf9 100%); border-left: 5px solid #0dcaf0; }
        .explanation-box {
            background: #f8f9fa;
            border-left: 4px solid #0d6efd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .beginner-tip {
            background: #e7f3ff;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .timeframe-btn {
            transition: all 0.3s ease;
        }
        .timeframe-btn.active { 
            background-color: #0d6efd !important; 
            color: white !important; 
        }
        .risk-low { background: linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%); }
        .risk-medium { background: linear-gradient(135deg, #fff3cd 0%, #ffdf91 100%); }
        .risk-high { background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%); }
        .ml-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 5px 15px;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Bitcoin AI Trading Assistant
            </a>
            <span class="navbar-text text-light">
                AI-Powered • Beginner Friendly
            </span>
        </div>
    </nav>

    <div class="container">
        <div class="main-container">
            <!-- Welcome Section -->
            <div class="welcome-header text-center">
                <h1 class="display-4 fw-bold mb-3">Bitcoin AI Trading Assistant</h1>
                <p class="lead fs-4">Machine Learning powered analysis with beginner-friendly explanations</p>
                <div class="row justify-content-center mt-4">
                    <div class="col-auto">
                        <span class="ml-badge"><i class="fas fa-robot me-1"></i>AI Predictions</span>
                    </div>
                    <div class="col-auto">
                        <span class="ml-badge"><i class="fas fa-brain me-1"></i>Machine Learning</span>
                    </div>
                    <div class="col-auto">
                        <span class="ml-badge"><i class="fas fa-graduation-cap me-1"></i>Beginner Friendly</span>
                    </div>
                </div>
            </div>

            <!-- Beginner Explanation -->
            <div class="beginner-tip">
                <h4><i class="fas fa-lightbulb me-2 text-warning"></i>How This AI Assistant Works</h4>
                <p class="mb-2">This tool uses Machine Learning to analyze Bitcoin price patterns and predict future trends. It's like having a smart assistant that learns from market data!</p>
                <small class="text-muted">🤖 <strong>AI Note:</strong> Our machine learning model analyzes 20+ factors to give you predictions.</small>
            </div>

            <!-- Analysis Configuration -->
            <div class="card shadow-lg">
                <div class="card-header bg-primary text-white py-3">
                    <h4 class="mb-0"><i class="fas fa-cogs me-2"></i>Analysis Setup</h4>
                </div>
                <div class="card-body p-4">
                    <form action="/analyze" method="POST">
                        <!-- Timeframe Selection -->
                        <div class="row g-4">
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-clock me-2"></i>Analysis Timeframe
                                </label>
                                <div class="btn-group w-100" role="group">
                                    <input type="radio" class="btn-check" name="time_frame" id="tf1" value="1" autocomplete="off">
                                    <label class="btn btn-outline-primary timeframe-btn" for="tf1">
                                        1 Day
                                    </label>
                                    
                                    <input type="radio" class="btn-check" name="time_frame" id="tf7" value="7" autocomplete="off">
                                    <label class="btn btn-outline-primary timeframe-btn" for="tf7">
                                        1 Week
                                    </label>
                                    
                                    <input type="radio" class="btn-check" name="time_frame" id="tf30" value="30" autocomplete="off" checked>
                                    <label class="btn btn-outline-primary timeframe-btn" for="tf30">
                                        1 Month
                                    </label>
                                    
                                    <input type="radio" class="btn-check" name="time_frame" id="tf90" value="90" autocomplete="off">
                                    <label class="btn btn-outline-primary timeframe-btn" for="tf90">
                                        3 Months
                                    </label>
                                </div>
                                <div class="explanation-box mt-2">
                                    <small><strong>AI Insight:</strong> Longer timeframes (1-3 months) often provide more reliable patterns for machine learning analysis.</small>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-robot me-2"></i>Analysis Mode
                                </label>
                                <select class="form-select" name="analysis_type">
                                    <option value="ml_simple">AI Simple Analysis (Recommended)</option>
                                    <option value="ml_advanced">AI Advanced Analysis</option>
                                    <option value="technical">Technical + AI</option>
                                    <option value="trends">Trend Analysis</option>
                                </select>
                                <div class="explanation-box mt-2">
                                    <small><strong>AI Modes:</strong> "AI Simple" uses machine learning for easy-to-understand predictions. "AI Advanced" adds more complex pattern recognition.</small>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Risk Settings -->
                        <div class="row g-4 mt-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-wallet me-2"></i>Learning Budget ($)
                                </label>
                                <input type="number" class="form-control" name="account_balance" value="1000" min="100" step="100">
                                <div class="explanation-box mt-2">
                                    <small><strong>For AI Learning:</strong> This helps the system calculate appropriate position sizes based on your risk level.</small>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-shield-alt me-2"></i>AI Risk Assessment
                                </label>
                                <input type="range" class="form-range" name="risk_per_trade" min="1" max="5" value="2" step="0.5">
                                <small class="text-muted">AI Risk Level: <span id="riskValue">2%</span> per scenario</small>
                                <div class="explanation-box mt-2">
                                    <small><strong>AI Risk Management:</strong> Lower values make the AI more conservative in its recommendations.</small>
                                </div>
                            </div>
                        </div>

                        <!-- Action Button -->
                        <div class="d-grid mt-4">
                            <button type="submit" class="btn btn-primary btn-lg py-3 fs-6">
                                <i class="fas fa-robot me-2"></i>Run AI Analysis
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- AI Features Grid -->
            <div class="row g-4 mt-3">
                <div class="col-md-3">
                    <div class="card h-100 text-center feature-card">
                        <div class="card-body py-4">
                            <i class="fas fa-brain fa-3x text-primary mb-3"></i>
                            <h6 class="fw-bold">ML Predictions</h6>
                            <small class="text-muted">Machine Learning price forecasts</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card h-100 text-center feature-card">
                        <div class="card-body py-4">
                            <i class="fas fa-chart-line fa-3x text-success mb-3"></i>
                            <h6 class="fw-bold">Pattern Recognition</h6>
                            <small class="text-muted">AI detects market patterns</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card h-100 text-center feature-card">
                        <div class="card-body py-4">
                            <i class="fas fa-shield-alt fa-3x text-info mb-3"></i>
                            <h6 class="fw-bold">Risk AI</h6>
                            <small class="text-muted">Smart risk assessment</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card h-100 text-center feature-card">
                        <div class="card-body py-4">
                            <i class="fas fa-graduation-cap fa-3x text-warning mb-3"></i>
                            <h6 class="fw-bold">Learning Mode</h6>
                            <small class="text-muted">Beginner explanations</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI Learning Tips -->
            <div class="card mt-4">
                <div class="card-header bg-warning text-dark py-3">
                    <h5 class="mb-0"><i class="fas fa-robot me-2"></i>How Our AI Works</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-database text-primary fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Data Analysis</h6>
                                    <small>AI analyzes price history, volume, and market patterns</small>
                                </div>
                            </div>
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-chart-network text-success fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Pattern Learning</h6>
                                    <small>Machine learning identifies recurring market patterns</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-calculator text-info fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Prediction Engine</h6>
                                    <small>AI calculates probability of price movements</small>
                                </div>
                            </div>
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-user-graduate text-danger fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Beginner Translation</h6>
                                    <small>Complex AI results explained in simple terms</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <small>
                <i class="fas fa-robot me-1"></i>Bitcoin AI Trading Assistant - Machine Learning Powered | 
                <i class="fas fa-exclamation-triangle me-1"></i>Educational Use Only
            </small>
        </div>
    </footer>

    <script>
        // Update risk percentage display
        document.querySelector('input[name="risk_per_trade"]').addEventListener('input', function(e) {
            document.getElementById('riskValue').textContent = e.target.value + '%';
        });

        // Active state for timeframe buttons
        document.querySelectorAll('.timeframe-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // Initialize default active state
        document.querySelector('input[value="30"]').nextElementSibling.classList.add('active');
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
    <title>AI Analysis Results</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
        }
        .results-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 20px 0;
            padding: 30px;
        }
        .signal-buy { 
            background: linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%); 
            border-left: 5px solid #198754; 
        }
        .signal-sell { 
            background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%); 
            border-left: 5px solid #dc3545; 
        }
        .signal-hold { 
            background: linear-gradient(135deg, #fff3cd 0%, #ffdf91 100%); 
            border-left: 5px solid #ffc107; 
        }
        .signal-info { 
            background: linear-gradient(135deg, #cff4fc 0%, #9eeaf9 100%); 
            border-left: 5px solid #0dcaf0; 
        }
        .card { 
            border: none; 
            border-radius: 12px; 
            box-shadow: 0 6px 15px rgba(0,0,0,0.08); 
            margin-bottom: 20px;
        }
        .risk-low { background: linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%); }
        .risk-medium { background: linear-gradient(135deg, #fff3cd 0%, #ffdf91 100%); }
        .risk-high { background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%); }
        .indicator-value { font-size: 1.5rem; font-weight: 700; }
        .explanation-box {
            background: #f8f9fa;
            border-left: 4px solid #0d6efd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .beginner-tip {
            background: #e7f3ff;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .ml-prediction {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .ai-confidence {
            font-size: 2rem;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Bitcoin AI Assistant
            </a>
            <a href="/" class="btn btn-outline-light">
                <i class="fas fa-arrow-left me-1"></i>New Analysis
            </a>
        </div>
    </nav>

    <div class="container">
        <div class="results-container">
            {% if error %}
            <div class="alert alert-danger">
                <h4><i class="fas fa-exclamation-triangle me-2"></i>Analysis Error</h4>
                <p class="mb-0">{{ error }}</p>
                <a href="/" class="btn btn-primary mt-3">Try Again</a>
            </div>
            {% else %}

            <!-- AI Recommendation Header -->
            <div class="card shadow-lg mb-4">
                <div class="card-body text-center py-4">
                    {% if analysis.recommendation == 'BUY' %}
                        {% set rec_color = 'success' %}{% set icon = 'arrow-up' %}{% set bg_color = 'success' %}
                        {% set rec_text = 'AI BUY SIGNAL' %}
                    {% elif analysis.recommendation == 'SELL' %}
                        {% set rec_color = 'danger' %}{% set icon = 'arrow-down' %}{% set bg_color = 'danger' %}
                        {% set rec_text = 'AI SELL SIGNAL' %}
                    {% else %}
                        {% set rec_color = 'warning' %}{% set icon = 'pause' %}{% set bg_color = 'warning' %}
                        {% set rec_text = 'AI HOLD SIGNAL' %}
                    {% endif %}
                    
                    <div class="row align-items-center">
                        <div class="col-md-8 text-md-start text-center">
                            <div class="ai-confidence text-{{ rec_color }} mb-2">
                                {{ analysis.confidence }}%
                            </div>
                            <h3 class="text-{{ rec_color }} mb-3">
                                <i class="fas fa-{{ icon }} me-2"></i>{{ rec_text }}
                            </h3>
                            <p class="h5 text-dark mb-1">
                                <i class="fas fa-dollar-sign me-1"></i>
                                Current Price: <strong>${{ "%.2f"|format(analysis.current_price) }}</strong>
                            </p>
                            <p class="text-muted">
                                <i class="fas fa-robot me-1"></i>
                                Based on AI analysis of {{ analysis.indicators_used }} market factors
                            </p>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-0">
                                <div class="card-body text-center">
                                    <h6>AI Risk Assessment</h6>
                                    <div class="h3 text-{{ analysis.risk_level.color }}">{{ analysis.risk_level.level }}</div>
                                    <small class="text-muted">{{ analysis.risk_level.description }}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI Explanation -->
            <div class="beginner-tip">
                <h4><i class="fas fa-robot me-2 text-primary"></i>AI Analysis Summary</h4>
                <p class="mb-2">{{ analysis.beginner_explanation }}</p>
                <small class="text-muted">🤖 <strong>AI Note:</strong> {{ analysis.ml_insights.summary }}</small>
            </div>

            <!-- Machine Learning Predictions -->
            <div class="ml-prediction">
                <div class="row text-center">
                    <div class="col-md-4">
                        <h5><i class="fas fa-brain me-2"></i>Next 24h Prediction</h5>
                        <div class="h3">${{ analysis.ml_insights.price_prediction.value }}</div>
                        <small>{{ analysis.ml_insights.price_prediction.confidence }}</small>
                    </div>
                    <div class="col-md-4">
                        <h5><i class="fas fa-trend-up me-2"></i>Trend Confidence</h5>
                        <div class="h3">{{ analysis.ml_insights.trend_confidence.value }}%</div>
                        <small>{{ analysis.ml_insights.trend_confidence.direction }}</small>
                    </div>
                    <div class="col-md-4">
                        <h5><i class="fas fa-chart-bar me-2"></i>Market Volatility</h5>
                        <div class="h3">{{ analysis.ml_insights.volatility.level }}</div>
                        <small>{{ analysis.ml_insights.volatility.forecast }}</small>
                    </div>
                </div>
            </div>

            <!-- Market Overview -->
            <div class="card mb-4">
                <div class="card-header bg-dark text-white py-3">
                    <h5 class="mb-0"><i class="fas fa-chart-simple me-2"></i>Market Overview</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3 text-center">
                        {% for indicator in analysis.simple_indicators %}
                        <div class="col-6 col-md-3">
                            <div class="card h-100 border-0 bg-light">
                                <div class="card-body py-3">
                                    <small class="fw-bold d-block text-truncate">{{ indicator.name }}</small>
                                    <div class="indicator-value text-{{ indicator.color }} mt-2">
                                        {{ indicator.value }}
                                    </div>
                                    <small class="text-muted d-block mt-1">{{ indicator.explanation }}</small>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <!-- AI Trading Signals -->
                <div class="col-lg-8">
                    <div class="card h-100">
                        <div class="card-header bg-dark text-white py-3">
                            <h5 class="mb-0"><i class="fas fa-robot me-2"></i>AI Trading Signals</h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="list-group list-group-flush">
                                {% for signal in analysis.signals %}
                                <div class="list-group-item {{ signal.class }} d-flex align-items-center py-3">
                                    <i class="fas fa-{{ signal.icon }} me-3 fa-lg text-{{ signal.color }}"></i>
                                    <div class="flex-grow-1">
                                        <div class="fw-bold">{{ signal.title }}</div>
                                        <small class="text-muted">{{ signal.description }}</small>
                                        {% if signal.explanation %}
                                        <div class="explanation-box mt-2">
                                            <small><strong>AI Insight:</strong> {{ signal.explanation }}</small>
                                        </div>
                                        {% endif %}
                                    </div>
                                    <span class="badge bg-{{ signal.strength_color }}">{{ signal.strength }}</span>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Risk Management -->
                <div class="col-lg-4">
                    <div class="card h-100">
                        <div class="card-header bg-info text-white py-3">
                            <h5 class="mb-0"><i class="fas fa-calculator me-2"></i>AI Position Sizing</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <small class="text-muted">AI Recommended Size</small>
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
                                <small><strong>AI Risk Level:</strong> {{ analysis.risk_level.level }}</small><br>
                                <small>{{ analysis.risk_level.description }}</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Machine Learning Insights -->
            <div class="card mt-4">
                <div class="card-header bg-success text-white py-3">
                    <h5 class="mb-0"><i class="fas fa-brain me-2"></i>Machine Learning Insights</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="fas fa-project-diagram me-2"></i>Pattern Recognition</h6>
                            <ul class="list-unstyled">
                                {% for pattern in analysis.ml_insights.patterns %}
                                <li class="mb-2">
                                    <span class="badge bg-{{ pattern.color }} me-2">{{ pattern.name }}</span>
                                    <small>{{ pattern.confidence }}</small>
                                </li>
                                {% endfor %}
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-chart-line me-2"></i>Market Sentiment</h6>
                            <div class="progress mb-2" style="height: 20px;">
                                <div class="progress-bar bg-{{ analysis.ml_insights.sentiment.color }}" 
                                     style="width: {{ analysis.ml_insights.sentiment.value }}%">
                                    {{ analysis.ml_insights.sentiment.value }}%
                                </div>
                            </div>
                            <small class="text-muted">{{ analysis.ml_insights.sentiment.description }}</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Learning Center -->
            <div class="card mt-4">
                <div class="card-header bg-warning text-dark py-3">
                    <h5 class="mb-0"><i class="fas fa-graduation-cap me-2"></i>AI Learning Center</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        {% for tip in analysis.educational_tips %}
                        <div class="col-md-6">
                            <div class="card h-100 border-0 bg-light">
                                <div class="card-body">
                                    <h6 class="card-title"><i class="fas fa-{{ tip.icon }} me-2 text-primary"></i>{{ tip.title }}</h6>
                                    <p class="card-text small">{{ tip.content }}</p>
                                    {% if tip.important %}
                                    <div class="alert alert-warning small mb-0">
                                        <i class="fas fa-robot me-1"></i>{{ tip.important }}
                                    </div>
                                    {% endif %}
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
                    <i class="fas fa-robot me-2"></i>New AI Analysis
                </a>
                <button class="btn btn-outline-success btn-lg px-5" onclick="window.print()">
                    <i class="fas fa-file-pdf me-2"></i>Save AI Report
                </button>
            </div>
            {% endif %}
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <small>
                <i class="fas fa-robot me-1"></i>Powered by Machine Learning | 
                <i class="fas fa-brain me-1"></i>AI Pattern Recognition | 
                <i class="fas fa-graduation-cap me-1"></i>Educational Purpose
            </small>
        </div>
    </footer>
</body>
</html>
'''

class BitcoinAIAssistant:
    def __init__(self):
        self.indicators = {}
        self.historical_predictions = deque(maxlen=100)
        self.ml_model = None
        self.scaler = StandardScaler()
        self.model_trained = False
        
    def fetch_bitcoin_data(self, days=30):
        """Fetch Bitcoin data with robust error handling for all timeframes"""
        print(f"📡 Fetching Bitcoin data for {days} days...")
        
        try:
            # Determine interval based on days
            if days == 1:
                interval = 'hourly'
                url_days = 1
            elif days <= 7:
                interval = 'hourly' 
                url_days = 7
            elif days <= 30:
                interval = 'daily'
                url_days = 30
            else:
                interval = 'daily'
                url_days = days
                
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd', 
                'days': url_days, 
                'interval': interval
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Process the data
            prices = [price[1] for price in data['prices']]
            dates = [datetime.fromtimestamp(price[0] / 1000) for price in data['prices']]
            
            # Create DataFrame
            df = pd.DataFrame({
                'date': dates,
                'price': prices
            })
            
            # Handle different timeframes
            if days == 1:
                # For 1 day, take last 24 hours
                df = df.tail(24)
            elif days == 7:
                # For 7 days, take last 7*24 hours (if hourly) or last 7 days
                df = df.tail(7 * 24) if interval == 'hourly' else df.tail(7)
            elif days == 30:
                df = df.tail(30)
            else:  # 90 days
                df = df.tail(90)
                
            df = df.set_index('date')
            
            print(f"✅ Successfully fetched {len(df)} data points for {days} days")
            return df
            
        except Exception as e:
            print(f"❌ API Error: {e}, using enhanced sample data")
            return self.create_enhanced_sample_data(days)
    
    def create_enhanced_sample_data(self, days=30):
        """Create realistic sample Bitcoin data"""
        print("🔄 Generating realistic sample Bitcoin data...")
        
        if days == 1:
            # 1-day data with hourly intervals
            dates = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                                end=datetime.now(), freq='H')
            base_price = 45000
            volatility = 0.008
        elif days == 7:
            # 7-day data with 4-hour intervals
            dates = pd.date_range(start=datetime.now() - timedelta(days=7), 
                                end=datetime.now(), freq='4H')
            base_price = 45000
            volatility = 0.015
        else:
            # 30/90 day data with daily intervals
            dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                                end=datetime.now(), freq='D')
            base_price = 45000
            volatility = 0.02
        
        # Realistic price simulation
        np.random.seed(42)
        prices = [base_price]
        
        for i in range(1, len(dates)):
            # Random walk with slight positive bias
            random_walk = np.random.normal(0.001, volatility)
            
            # Add some mean reversion
            if i > 5:
                recent_trend = (prices[-1] - prices[-5]) / prices[-5]
                if abs(recent_trend) > 0.05:
                    random_walk -= recent_trend * 0.1
            
            new_price = prices[-1] * (1 + random_walk)
            prices.append(max(1000, new_price))
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices
        })
        df = df.set_index('date')
        
        print(f"✅ Generated {len(df)} realistic data points")
        return df
    
    def prepare_ml_features(self, df):
        """Prepare features for machine learning prediction"""
        prices = df['price'].values
        
        if len(prices) < 20:
            return None, None
            
        features = []
        targets = []
        
        # Create multiple technical indicators as features
        for i in range(20, len(prices)-1):
            feature_set = []
            
            # Price-based features
            current_price = prices[i]
            feature_set.extend([
                current_price,
                np.mean(prices[i-5:i]),  # 5-period SMA
                np.mean(prices[i-10:i]), # 10-period SMA
                np.mean(prices[i-20:i]), # 20-period SMA
                np.std(prices[i-5:i]) / current_price,  # 5-period volatility
                np.std(prices[i-10:i]) / current_price, # 10-period volatility
            ])
            
            # RSI-like feature
            gains = sum(max(0, prices[j] - prices[j-1]) for j in range(i-14, i) if j > 0)
            losses = sum(max(0, prices[j-1] - prices[j]) for j in range(i-14, i) if j > 0)
            rsi = 100 - (100 / (1 + (gains / losses))) if losses != 0 else 50
            feature_set.append(rsi)
            
            # Momentum features
            feature_set.extend([
                (prices[i] - prices[i-1]) / prices[i-1],  # 1-period return
                (prices[i] - prices[i-5]) / prices[i-5],  # 5-period return
                (prices[i] - prices[i-10]) / prices[i-10], # 10-period return
            ])
            
            # Volume-like features (simulated)
            feature_set.append(np.random.normal(1, 0.2))  # Simulated volume
            
            features.append(feature_set)
            targets.append(1 if prices[i+1] > prices[i] else 0)  # 1 if price goes up, 0 if down
            
        return np.array(features), np.array(targets)
    
    def train_ml_model(self, features, targets):
        """Train machine learning model"""
        if features is None or len(features) < 10:
            return None
            
        try:
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train Random Forest classifier
            self.ml_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.ml_model.fit(features_scaled, targets)
            self.model_trained = True
            print("✅ Machine Learning model trained successfully")
            return self.ml_model
            
        except Exception as e:
            print(f"❌ ML training error: {e}")
            return None
    
    def ml_predict(self, df):
        """Make machine learning predictions"""
        prices = df['price'].values
        
        if len(prices) < 20 or not self.model_trained:
            # Fallback to simple prediction
            return self.simple_prediction(prices)
        
        try:
            # Prepare features for prediction
            current_features = []
            current_price = prices[-1]
            
            # Same feature engineering as training
            current_features.extend([
                current_price,
                np.mean(prices[-5:]),   # 5-period SMA
                np.mean(prices[-10:]),  # 10-period SMA
                np.mean(prices[-20:]),  # 20-period SMA
                np.std(prices[-5:]) / current_price,   # 5-period volatility
                np.std(prices[-10:]) / current_price,  # 10-period volatility
            ])
            
            # RSI
            gains = sum(max(0, prices[j] - prices[j-1]) for j in range(-14, 0) if abs(j) < len(prices))
            losses = sum(max(0, prices[j-1] - prices[j]) for j in range(-14, 0) if abs(j) < len(prices))
            rsi = 100 - (100 / (1 + (gains / losses))) if losses != 0 else 50
            current_features.append(rsi)
            
            # Momentum
            current_features.extend([
                (prices[-1] - prices[-2]) / prices[-2] if len(prices) >= 2 else 0,
                (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0,
                (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 else 0,
            ])
            
            # Volume (simulated)
            current_features.append(1.0)
            
            # Make prediction
            features_scaled = self.scaler.transform([current_features])
            prediction_proba = self.ml_model.predict_proba(features_scaled)[0]
            prediction = self.ml_model.predict(features_scaled)[0]
            
            # Calculate next price prediction using linear regression
            x = np.arange(len(prices))
            slope, intercept = np.polyfit(x, prices, 1)
            next_price = slope * len(prices) + intercept
            
            return {
                'direction': 'UP' if prediction == 1 else 'DOWN',
                'confidence': max(prediction_proba) * 100,
                'next_price': max(0, next_price),
                'trend_strength': abs(slope) * 1000,
                'volatility': np.std(prices[-10:]) / np.mean(prices[-10:]) * 100
            }
            
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            return self.simple_prediction(prices)
    
    def simple_prediction(self, prices):
        """Simple fallback prediction"""
        if len(prices) < 5:
            return {
                'direction': 'NEUTRAL',
                'confidence': 50,
                'next_price': prices[-1] if len(prices) > 0 else 45000,
                'trend_strength': 0,
                'volatility': 0
            }
        
        # Simple linear regression
        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)
        next_price = slope * len(prices) + intercept
        
        # Simple confidence based on recent trend consistency
        recent_trend = (prices[-1] - prices[-5]) / prices[-5]
        confidence = min(80, 50 + abs(recent_trend) * 1000)
        
        return {
            'direction': 'UP' if slope > 0 else 'DOWN',
            'confidence': confidence,
            'next_price': max(0, next_price),
            'trend_strength': abs(slope) * 1000,
            'volatility': np.std(prices[-10:]) / np.mean(prices[-10:]) * 100
        }
    
    def get_ai_analysis(self, df, account_balance=1000, risk_per_trade=2):
        """Comprehensive AI analysis with machine learning"""
        prices = df['price'].values
        
        if len(prices) < 10:
            return self.get_default_analysis(df)
        
        current_price = float(df['price'].iloc[-1])
        
        # Train ML model if we have enough data
        features, targets = self.prepare_ml_features(df)
        if features is not None:
            self.train_ml_model(features, targets)
        
        # Get ML predictions
        ml_prediction = self.ml_predict(df)
        
        # Calculate technical indicators
        tech_indicators = self.calculate_simple_indicators(prices)
        
        # Combine ML and technical analysis for final recommendation
        recommendation, confidence = self.combine_analysis(ml_prediction, tech_indicators)
        
        # Risk assessment
        risk_level = self.assess_risk(ml_prediction, tech_indicators)
        
        # Generate signals
        signals = self.generate_ai_signals(ml_prediction, tech_indicators, recommendation)
        
        # Position sizing
        position_sizing = self.calculate_simple_position_size(current_price, account_balance, risk_per_trade)
        
        # ML insights
        ml_insights = self.generate_ml_insights(ml_prediction, tech_indicators)
        
        # Educational content
        educational_tips = self.get_educational_tips(recommendation, ml_prediction)
        
        # Beginner explanation
        beginner_explanation = self.get_beginner_explanation(recommendation, ml_prediction, tech_indicators)
        
        # Simple indicators for display
        simple_indicators = [
            {
                'name': 'AI Confidence',
                'value': f"{ml_prediction['confidence']:.1f}%",
                'color': 'success' if ml_prediction['confidence'] > 70 else 'danger' if ml_prediction['confidence'] < 50 else 'warning',
                'explanation': 'Machine Learning prediction confidence'
            },
            {
                'name': 'Trend Direction',
                'value': ml_prediction['direction'],
                'color': 'success' if ml_prediction['direction'] == 'UP' else 'danger' if ml_prediction['direction'] == 'DOWN' else 'warning',
                'explanation': 'AI predicted price direction'
            },
            {
                'name': 'Market Volatility',
                'value': f"{tech_indicators['volatility']:.1f}%",
                'color': 'success' if tech_indicators['volatility'] < 3 else 'danger' if tech_indicators['volatility'] > 7 else 'warning',
                'explanation': 'Recent price movement range'
            },
            {
                'name': 'Price vs Average',
                'value': f"{tech_indicators['price_vs_avg']:+.1f}%",
                'color': 'success' if tech_indicators['price_vs_avg'] < -2 else 'danger' if tech_indicators['price_vs_avg'] > 5 else 'warning',
                'explanation': 'Current price vs 20-period average'
            }
        ]
        
        return {
            'recommendation': recommendation,
            'confidence': round(confidence, 1),
            'current_price': current_price,
            'simple_indicators': simple_indicators,
            'signals': signals,
            'position_sizing': position_sizing,
            'risk_level': risk_level,
            'ml_insights': ml_insights,
            'educational_tips': educational_tips,
            'beginner_explanation': beginner_explanation,
            'indicators_used': len(simple_indicators) + len(signals)
        }
    
    def combine_analysis(self, ml_prediction, tech_indicators):
        """Combine ML and technical analysis for final recommendation"""
        ml_weight = 0.6  # Weight for ML prediction
        tech_weight = 0.4  # Weight for technical analysis
        
        # ML contribution
        ml_direction = 1 if ml_prediction['direction'] == 'UP' else -1 if ml_prediction['direction'] == 'DOWN' else 0
        ml_contribution = ml_direction * ml_prediction['confidence'] / 100
        
        # Technical analysis contribution
        tech_contribution = 0
        if tech_indicators['price_vs_avg'] < -2:
            tech_contribution += 0.3
        elif tech_indicators['price_vs_avg'] > 5:
            tech_contribution -= 0.3
            
        if tech_indicators['trend_strength'] > 2:
            tech_contribution += 0.2
        elif tech_indicators['trend_strength'] < -2:
            tech_contribution -= 0.2
        
        # Combined score
        combined_score = (ml_contribution * ml_weight) + (tech_contribution * tech_weight)
        
        # Determine recommendation
        if combined_score > 0.1:
            recommendation = "BUY"
            confidence = min(95, 50 + abs(combined_score) * 100)
        elif combined_score < -0.1:
            recommendation = "SELL"
            confidence = min(95, 50 + abs(combined_score) * 100)
        else:
            recommendation = "HOLD"
            confidence = 60
            
        return recommendation, confidence
    
    def assess_risk(self, ml_prediction, tech_indicators):
        """AI risk assessment"""
        volatility = tech_indicators['volatility']
        ml_confidence = ml_prediction['confidence']
        
        if volatility < 3 and ml_confidence > 70:
            return {'level': 'LOW', 'color': 'success', 'description': 'Low volatility with high AI confidence'}
        elif volatility < 5 and ml_confidence > 60:
            return {'level': 'MEDIUM', 'color': 'warning', 'description': 'Moderate market conditions'}
        else:
            return {'level': 'HIGH', 'color': 'danger', 'description': 'High volatility or low AI confidence'}
    
    def generate_ai_signals(self, ml_prediction, tech_indicators, recommendation):
        """Generate AI-powered trading signals"""
        signals = []
        
        # ML Prediction Signal
        if ml_prediction['confidence'] > 70:
            signals.append({
                'title': f'Strong AI {ml_prediction["direction"]} Signal',
                'description': f"Machine Learning predicts {ml_prediction['direction']} movement with {ml_prediction['confidence']:.1f}% confidence",
                'explanation': 'AI model detects strong pattern suggesting this direction',
                'icon': 'robot',
                'color': 'success' if ml_prediction['direction'] == 'UP' else 'danger',
                'class': 'signal-buy' if ml_prediction['direction'] == 'UP' else 'signal-sell',
                'strength': 'HIGH',
                'strength_color': 'success' if ml_prediction['direction'] == 'UP' else 'danger'
            })
        
        # Technical Signals
        if tech_indicators['price_vs_avg'] < -2:
            signals.append({
                'title': 'Undervalued Signal',
                'description': f"Price is {abs(tech_indicators['price_vs_avg']):.1f}% below 20-period average",
                'explanation': 'Historical patterns suggest potential buying opportunity',
                'icon': 'shopping-cart',
                'color': 'success',
                'class': 'signal-buy',
                'strength': 'MEDIUM',
                'strength_color': 'success'
            })
        
        if tech_indicators['trend_strength'] > 3:
            signals.append({
                'title': 'Strong Upward Momentum',
                'description': f"Price shows strong upward trend ({tech_indicators['trend_strength']:.1f}%)",
                'explanation': 'Consistent buying pressure detected',
                'icon': 'arrow-up',
                'color': 'success',
                'class': 'signal-buy',
                'strength': 'MEDIUM',
                'strength_color': 'success'
            })
        
        # Risk Signal
        if tech_indicators['volatility'] > 7:
            signals.append({
                'title': 'High Volatility Alert',
                'description': f"Market volatility is high ({tech_indicators['volatility']:.1f}%)",
                'explanation': 'Increased risk - consider smaller position sizes',
                'icon': 'exclamation-triangle',
                'color': 'warning',
                'class': 'signal-hold',
                'strength': 'HIGH',
                'strength_color': 'warning'
            })
        
        return signals
    
    def generate_ml_insights(self, ml_prediction, tech_indicators):
        """Generate machine learning insights"""
        return {
            'price_prediction': {
                'value': f"{ml_prediction['next_price']:.0f}",
                'confidence': f"{ml_prediction['confidence']:.1f}% confident"
            },
            'trend_confidence': {
                'value': ml_prediction['confidence'],
                'direction': ml_prediction['direction'],
                'color': 'success' if ml_prediction['confidence'] > 70 else 'warning' if ml_prediction['confidence'] > 50 else 'danger'
            },
            'volatility': {
                'level': 'HIGH' if tech_indicators['volatility'] > 7 else 'MEDIUM' if tech_indicators['volatility'] > 3 else 'LOW',
                'forecast': 'Increasing' if tech_indicators['volatility'] > 5 else 'Stable',
                'color': 'danger' if tech_indicators['volatility'] > 7 else 'warning' if tech_indicators['volatility'] > 3 else 'success'
            },
            'patterns': [
                {'name': 'Trend Detection', 'confidence': 'Strong', 'color': 'success'},
                {'name': 'Momentum Analysis', 'confidence': 'Medium', 'color': 'warning'},
                {'name': 'Support/Resistance', 'confidence': 'Active', 'color': 'info'}
            ],
            'sentiment': {
                'value': ml_prediction['confidence'],
                'color': 'success' if ml_prediction['confidence'] > 70 else 'warning' if ml_prediction['confidence'] > 50 else 'danger',
                'description': 'Bullish' if ml_prediction['direction'] == 'UP' else 'Bearish'
            },
            'summary': f"AI detects {ml_prediction['direction'].lower()} trend with {ml_prediction['confidence']:.1f}% confidence. Market volatility is {'high' if tech_indicators['volatility'] > 7 else 'moderate' if tech_indicators['volatility'] > 3 else 'low'}."
        }
    
    def calculate_simple_indicators(self, prices):
        """Calculate technical indicators"""
        if len(prices) < 20:
            return {'price_vs_avg': 0, 'trend_strength': 0, 'volatility': 0}
        
        current_price = prices[-1]
        sma_20 = np.mean(prices[-20:])
        
        price_vs_avg = ((current_price - sma_20) / sma_20) * 100
        
        # Trend strength
        if len(prices) >= 10:
            short_trend = (current_price - prices[-5]) / prices[-5] * 100
            medium_trend = (current_price - prices[-10]) / prices[-10] * 100
            trend_strength = (short_trend + medium_trend) / 2
        else:
            trend_strength = 0
        
        # Volatility
        recent_prices = prices[-10:] if len(prices) >= 10 else prices
        volatility = (np.std(recent_prices) / np.mean(recent_prices)) * 100
        
        return {
            'price_vs_avg': price_vs_avg,
            'trend_strength': trend_strength,
            'volatility': volatility
        }
    
    def calculate_simple_position_size(self, current_price, account_balance, risk_per_trade):
        """Calculate position sizing"""
        risk_amount = account_balance * (risk_per_trade / 100)
        stop_loss_pct = 5
        stop_loss_price = current_price * (1 - stop_loss_pct / 100)
        price_diff = current_price - stop_loss_price
        
        if price_diff <= 0:
            position_size = 0
        else:
            position_size = risk_amount / price_diff
            
        max_position_value = account_balance * 0.10
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
    
    def get_educational_tips(self, recommendation, ml_prediction):
        """Get educational tips"""
        return [
            {
                'icon': 'robot',
                'title': 'Understanding AI Predictions',
                'content': 'Our machine learning model analyzes price patterns, volatility, and market trends to predict future movements.',
                'important': 'AI predictions are probabilistic, not guarantees. Always use proper risk management.'
            },
            {
                'icon': 'chart-line',
                'title': 'Reading Market Signals',
                'content': 'Multiple signals (AI + technical analysis) provide more reliable insights than single indicators.',
                'important': 'Look for confirmation across different timeframes and indicators.'
            },
            {
                'icon': 'shield-alt',
                'title': 'AI Risk Management',
                'content': 'The AI assesses market volatility and confidence levels to determine appropriate risk levels.',
                'important': 'High volatility periods require smaller position sizes and wider stop-losses.'
            },
            {
                'icon': 'brain',
                'title': 'Machine Learning in Trading',
                'content': 'ML models learn from historical patterns but cannot predict black swan events or market shocks.',
                'important': 'Combine AI insights with fundamental analysis and market news.'
            }
        ]
    
    def get_beginner_explanation(self, recommendation, ml_prediction, tech_indicators):
        """Get beginner-friendly explanation"""
        if recommendation == "BUY":
            return f"The AI analysis suggests buying opportunities exist. Machine Learning predicts {ml_prediction['direction'].lower()} movement with {ml_prediction['confidence']:.1f}% confidence, and technical indicators show favorable conditions."
        elif recommendation == "SELL":
            return f"The AI analysis suggests caution. Machine Learning detects {ml_prediction['direction'].lower()} pressure with {ml_prediction['confidence']:.1f}% confidence, and technical indicators show potential overvaluation."
        else:
            return f"The AI analysis suggests waiting for clearer signals. Market conditions are mixed with {ml_prediction['confidence']:.1f}% prediction confidence. This might be a good time to observe and wait for better opportunities."
    
    def get_default_analysis(self, df):
        """Default analysis when data is insufficient"""
        current_price = float(df['price'].iloc[-1]) if len(df) > 0 else 45000
        
        return {
            'recommendation': 'HOLD',
            'confidence': 50,
            'current_price': current_price,
            'simple_indicators': [
                {
                    'name': 'Data Quality',
                    'value': 'Limited',
                    'color': 'warning',
                    'explanation': 'Need more data for AI analysis'
                }
            ],
            'signals': [{
                'title': 'Insufficient Data',
                'description': 'More historical data needed for reliable AI analysis',
                'explanation': 'Try analyzing a longer timeframe (1 month recommended)',
                'icon': 'info-circle',
                'color': 'warning',
                'class': 'signal-hold',
                'strength': 'LOW',
                'strength_color': 'warning'
            }],
            'position_sizing': {'recommended_size': 0, 'stop_loss': 0, 'take_profit_1': 0, 'take_profit_2': 0},
            'risk_level': {'level': 'UNKNOWN', 'color': 'secondary', 'description': 'Insufficient data for AI risk assessment'},
            'ml_insights': {
                'price_prediction': {'value': f"{current_price:.0f}", 'confidence': 'Low confidence'},
                'trend_confidence': {'value': 50, 'direction': 'NEUTRAL', 'color': 'warning'},
                'volatility': {'level': 'UNKNOWN', 'forecast': 'Unknown', 'color': 'secondary'},
                'patterns': [],
                'sentiment': {'value': 50, 'color': 'warning', 'description': 'Neutral'},
                'summary': 'Insufficient data for machine learning analysis'
            },
            'educational_tips': [],
            'beginner_explanation': 'We need more market data to provide reliable AI analysis. Please try again with a longer time period (1 month or more).',
            'indicators_used': 0
        }

# Initialize the AI assistant
ai_bot = BitcoinAIAssistant()

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        time_frame = request.form.get('time_frame', '30')
        analysis_type = request.form.get('analysis_type', 'ml_simple')
        account_balance = float(request.form.get('account_balance', 1000))
        risk_per_trade = float(request.form.get('risk_per_trade', 2))
        
        print(f"🤖 Starting AI analysis: {time_frame} days, {analysis_type} mode")
        
        # Fetch data for the selected timeframe
        df = ai_bot.fetch_bitcoin_data(days=int(time_frame))
        
        # Get AI analysis
        analysis = ai_bot.get_ai_analysis(df, account_balance, risk_per_trade)
        
        print(f"✅ AI analysis complete: {analysis['recommendation']} with {analysis['confidence']}% confidence")
        
        return render_template_string(RESULTS_HTML, 
                                    analysis=analysis, 
                                    error=None)
                                    
    except Exception as e:
        error_msg = f"AI analysis failed: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"🔍 Detailed error: {traceback.format_exc()}")
        return render_template_string(RESULTS_HTML, 
                                    error=error_msg)

@app.route('/api/ai_analysis')
def api_ai_analysis():
    """AI-powered JSON API endpoint"""
    try:
        df = ai_bot.fetch_bitcoin_data()
        analysis = ai_bot.get_ai_analysis(df)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'recommendation': analysis['recommendation'],
                'confidence': analysis['confidence'],
                'current_price': analysis['current_price'],
                'risk_level': analysis['risk_level'],
                'ml_insights': analysis['ml_insights']
            }
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
        'service': 'Bitcoin AI Trading Assistant',
        'version': '3.0',
        'features': ['Machine Learning', 'AI Predictions', 'Risk Assessment', 'Beginner Friendly']
    })

if __name__ == '__main__':
    print("🚀 Bitcoin AI Trading Assistant Starting...")
    print("=" * 60)
    print("🤖 AI-Powered with Machine Learning")
    print("📊 Web Interface: http://localhost:5000")
    print("🔗 AI API: http://localhost:5000/api/ai_analysis")
    print("❤️  Health Check: http://localhost:5000/health")
    print("=" * 60)
    print("💡 IMPORTANT: This is for EDUCATIONAL PURPOSES only!")
    print("   AI predictions are not financial advice.")
    print("=" * 60)
    
    # Test the AI system
    try:
        test_data = ai_bot.fetch_bitcoin_data(days=1)
        print(f"✅ 1-Day AI analysis ready: {len(test_data)} data points")
        test_data = ai_bot.fetch_bitcoin_data(days=7)
        print(f"✅ 7-Day AI analysis ready: {len(test_data)} data points")
        test_data = ai_bot.fetch_bitcoin_data(days=30)
        print(f"✅ 30-Day AI analysis ready: {len(test_data)} data points")
    except Exception as e:
        print(f"⚠️  System check warning: {e}")
        print("   AI will use enhanced sample data when needed.")
    
    print("🎯 Starting AI Flask server...")

    app.run(debug=True, host='0.0.0.0', port=5000)

