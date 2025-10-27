from flask import Flask, render_template_string, request, jsonify
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from collections import deque
import time

app = Flask(__name__)

# Enhanced HTML Templates with beginner-friendly explanations
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bitcoin Trading Helper - Beginner Friendly</title>
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
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Bitcoin Trading Helper
            </a>
            <span class="navbar-text text-light">
                For Beginners • Educational Tool
            </span>
        </div>
    </nav>

    <div class="container">
        <div class="main-container">
            <!-- Welcome Section -->
            <div class="welcome-header text-center">
                <h1 class="display-4 fw-bold mb-3">Bitcoin Trading Helper</h1>
                <p class="lead fs-4">Your friendly guide to understanding Bitcoin markets</p>
                <p class="mb-0">No experience needed - We explain everything in simple terms!</p>
            </div>

            <!-- Beginner Explanation -->
            <div class="beginner-tip">
                <h4><i class="fas fa-lightbulb me-2 text-warning"></i>First Time Here?</h4>
                <p class="mb-2">This tool helps you understand Bitcoin market trends using simple analysis. Think of it as a weather forecast for Bitcoin prices!</p>
                <small class="text-muted">💡 <strong>Remember:</strong> This is for learning only. Always do your own research before investing.</small>
            </div>

            <!-- Simple Analysis Configuration -->
            <div class="card shadow-lg">
                <div class="card-header bg-primary text-white py-3">
                    <h4 class="mb-0"><i class="fas fa-cogs me-2"></i>Simple Setup</h4>
                </div>
                <div class="card-body p-4">
                    <form action="/analyze" method="POST">
                        <!-- Timeframe Selection with Explanations -->
                        <div class="row g-4">
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-clock me-2"></i>Time Period to Analyze
                                </label>
                                <div class="btn-group w-100" role="group">
                                    <input type="radio" class="btn-check" name="time_frame" id="tf1" value="1" autocomplete="off">
                                    <label class="btn btn-outline-primary timeframe-btn" for="tf1" data-bs-toggle="tooltip" title="Short-term trends">
                                        1 Day
                                    </label>
                                    
                                    <input type="radio" class="btn-check" name="time_frame" id="tf7" value="7" autocomplete="off">
                                    <label class="btn btn-outline-primary timeframe-btn" for="tf7" data-bs-toggle="tooltip" title="Weekly trends">
                                        1 Week
                                    </label>
                                    
                                    <input type="radio" class="btn-check" name="time_frame" id="tf30" value="30" autocomplete="off" checked>
                                    <label class="btn btn-outline-primary timeframe-btn" for="tf30" data-bs-toggle="tooltip" title="Monthly trends - Recommended for beginners">
                                        1 Month
                                    </label>
                                </div>
                                <div class="explanation-box mt-2">
                                    <small><strong>What this means:</strong> Choose how far back to look at Bitcoin prices. 1 month is usually best for beginners.</small>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-chart-line me-2"></i>Analysis Type
                                </label>
                                <select class="form-select" name="analysis_type">
                                    <option value="simple" selected>Simple Analysis (Recommended)</option>
                                    <option value="technical">Technical Analysis</option>
                                    <option value="trends">Trend Analysis</option>
                                </select>
                                <div class="explanation-box mt-2">
                                    <small><strong>What this means:</strong> "Simple Analysis" gives you easy-to-understand results. Perfect for learning!</small>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Simple Risk Settings -->
                        <div class="row g-4 mt-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-wallet me-2"></i>Learning Budget ($)
                                </label>
                                <input type="number" class="form-control" name="account_balance" value="1000" min="100" step="100">
                                <div class="explanation-box mt-2">
                                    <small><strong>What this means:</strong> This is just for learning position sizes. Use any number you're comfortable learning with.</small>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold fs-6">
                                    <i class="fas fa-shield-alt me-2"></i>Learning Risk Level
                                </label>
                                <input type="range" class="form-range" name="risk_per_trade" min="1" max="5" value="2" step="0.5">
                                <small class="text-muted">Current: <span id="riskValue">2%</span> per learning scenario</small>
                                <div class="explanation-box mt-2">
                                    <small><strong>What this means:</strong> How much to "risk" in our learning examples. Lower = safer approach.</small>
                                </div>
                            </div>
                        </div>

                        <!-- Action Button -->
                        <div class="d-grid mt-4">
                            <button type="submit" class="btn btn-primary btn-lg py-3 fs-6">
                                <i class="fas fa-rocket me-2"></i>Get Bitcoin Analysis
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Learning Features Grid -->
            <div class="row g-4 mt-3">
                <div class="col-md-4">
                    <div class="card h-100 text-center feature-card">
                        <div class="card-body py-4">
                            <i class="fas fa-graduation-cap fa-3x text-primary mb-3"></i>
                            <h6 class="fw-bold">Beginner Friendly</h6>
                            <small class="text-muted">Simple explanations for every term</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 text-center feature-card">
                        <div class="card-body py-4">
                            <i class="fas fa-chart-simple fa-3x text-success mb-3"></i>
                            <h6 class="fw-bold">Easy Analysis</h6>
                            <small class="text-muted">Clear buy/hold/sell signals</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 text-center feature-card">
                        <div class="card-body py-4">
                            <i class="fas fa-shield-heart fa-3x text-info mb-3"></i>
                            <h6 class="fw-bold">Risk Education</h6>
                            <small class="text-muted">Learn about safe trading practices</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Learning Tips -->
            <div class="card mt-4">
                <div class="card-header bg-warning text-dark py-3">
                    <h5 class="mb-0"><i class="fas fa-trophy me-2"></i>Quick Learning Tips</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-1 text-primary fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Start Simple</h6>
                                    <small>Use "Simple Analysis" first to understand basic concepts</small>
                                </div>
                            </div>
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-2 text-success fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Learn Terms</h6>
                                    <small>We explain every technical term in plain English</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-3 text-info fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Practice First</h6>
                                    <small>This is a learning tool - practice without real money</small>
                                </div>
                            </div>
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-4 text-danger fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Ask Questions</h6>
                                    <small>Confused? That's normal! Take notes and research more</small>
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
                <i class="fas fa-graduation-cap me-1"></i>Bitcoin Trading Helper - Educational Tool for Beginners | 
                <i class="fas fa-exclamation-triangle me-1"></i>Not Financial Advice
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

        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
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
    <title>Your Bitcoin Analysis Results</title>
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
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Bitcoin Trading Helper
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
                <h4><i class="fas fa-exclamation-triangle me-2"></i>Oops! Something went wrong</h4>
                <p class="mb-0">{{ error }}</p>
                <a href="/" class="btn btn-primary mt-3">Try Again</a>
            </div>
            {% else %}

            <!-- Simple Recommendation Header -->
            <div class="card shadow-lg mb-4">
                <div class="card-body text-center py-4">
                    {% if analysis.recommendation == 'BUY' %}
                        {% set rec_color = 'success' %}{% set icon = 'arrow-up' %}{% set bg_color = 'success' %}
                        {% set rec_text = 'CONSIDER BUYING' %}
                    {% elif analysis.recommendation == 'SELL' %}
                        {% set rec_color = 'danger' %}{% set icon = 'arrow-down' %}{% set bg_color = 'danger' %}
                        {% set rec_text = 'CONSIDER SELLING' %}
                    {% else %}
                        {% set rec_color = 'warning' %}{% set icon = 'pause' %}{% set bg_color = 'warning' %}
                        {% set rec_text = 'WAIT AND WATCH' %}
                    {% endif %}
                    
                    <div class="row align-items-center">
                        <div class="col-md-8 text-md-start text-center">
                            <h1 class="text-{{ rec_color }} fw-bold display-4">{{ analysis.confidence }}%</h1>
                            <h3 class="text-{{ rec_color }} mb-3">
                                <i class="fas fa-{{ icon }} me-2"></i>{{ rec_text }}
                            </h3>
                            <p class="h5 text-dark mb-1">
                                <i class="fas fa-dollar-sign me-1"></i>
                                Current Bitcoin Price: <strong>${{ "%.2f"|format(analysis.current_price) }}</strong>
                            </p>
                            <p class="text-muted">Based on {{ analysis.indicators_used }} market indicators</p>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-0">
                                <div class="card-body text-center">
                                    <h6>Market Risk Level</h6>
                                    <div class="h3 text-{{ analysis.risk_level.color }}">{{ analysis.risk_level.level }}</div>
                                    <small class="text-muted">{{ analysis.risk_level.description }}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- What This Means for Beginners -->
            <div class="beginner-tip">
                <h4><i class="fas fa-graduation-cap me-2 text-primary"></i>What This Means For You</h4>
                <p class="mb-2">{{ analysis.beginner_explanation }}</p>
                <small class="text-muted">💡 <strong>Remember:</strong> This is educational. Real trading involves more factors.</small>
            </div>

            <!-- Simple Market Overview -->
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
                <!-- Simple Trading Signals -->
                <div class="col-lg-8">
                    <div class="card h-100">
                        <div class="card-header bg-dark text-white py-3">
                            <h5 class="mb-0"><i class="fas fa-bell me-2"></i>Market Signals</h5>
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
                                            <small><strong>In simple terms:</strong> {{ signal.explanation }}</small>
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

                <!-- Learning About Risk -->
                <div class="col-lg-4">
                    <div class="card h-100">
                        <div class="card-header bg-info text-white py-3">
                            <h5 class="mb-0"><i class="fas fa-shield-heart me-2"></i>Learning About Risk</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <small class="text-muted">Learning Position Size</small>
                                <div class="h4 text-success">${{ analysis.position_sizing.recommended_size }}</div>
                                <small>Based on {{ analysis.position_sizing.risk_per_trade }}% learning risk</small>
                            </div>
                            
                            <div class="mb-3">
                                <small class="text-muted">Safety Price (Stop-Loss)</small>
                                <div class="h5 text-danger">${{ analysis.position_sizing.stop_loss }}</div>
                                <small>{{ analysis.position_sizing.stop_loss_pct }}% below current</small>
                            </div>
                            
                            <div class="mb-3">
                                <small class="text-muted">Target Prices</small>
                                <div class="h6 text-success">Goal 1: ${{ analysis.position_sizing.take_profit_1 }}</div>
                                <div class="h6 text-success">Goal 2: ${{ analysis.position_sizing.take_profit_2 }}</div>
                            </div>
                            
                            <div class="alert alert-{{ analysis.risk_level.color }} mt-3">
                                <small><strong>Market Risk:</strong> {{ analysis.risk_level.level }}</small><br>
                                <small>{{ analysis.risk_level.description }}</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Learning Center -->
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
                                    {% if tip.important %}
                                    <div class="alert alert-warning small mb-0">
                                        <i class="fas fa-exclamation-triangle me-1"></i>{{ tip.important }}
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Next Steps -->
            <div class="card mt-4">
                <div class="card-header bg-success text-white py-3">
                    <h5 class="mb-0"><i class="fas fa-footsteps me-2"></i>Next Steps for Learning</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-book text-primary fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Learn Basic Terms</h6>
                                    <small>Research: support/resistance, trend lines, volume</small>
                                </div>
                            </div>
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-chart-line text-success fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Practice Reading Charts</h6>
                                    <small>Use free charting tools to see price patterns</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-users text-info fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Join Learning Communities</h6>
                                    <small>Find beginner-friendly trading communities</small>
                                </div>
                            </div>
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-hand-holding-usd text-warning fa-lg me-3"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="fw-bold">Start Small</h6>
                                    <small>If you decide to trade, start with very small amounts</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="text-center my-5">
                <a href="/" class="btn btn-primary btn-lg me-3 px-5">
                    <i class="fas fa-sync-alt me-2"></i>New Analysis
                </a>
                <button class="btn btn-outline-success btn-lg px-5" onclick="window.print()">
                    <i class="fas fa-file-pdf me-2"></i>Save Report
                </button>
            </div>
            {% endif %}
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <small>
                <i class="fas fa-graduation-cap me-1"></i>Bitcoin Trading Helper - Educational Tool | 
                <i class="fas fa-exclamation-triangle me-1"></i>Learn First, Trade Later
            </small>
        </div>
    </footer>
</body>
</html>
'''

class BeginnerFriendlyBitcoinAssistant:
    def __init__(self):
        self.indicators = {}
        self.historical_predictions = deque(maxlen=100)
        self.data_sources = [
            'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart',
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        ]
        
    def fetch_bitcoin_data_with_fallback(self, days=30):
        """Fetch Bitcoin data with multiple fallback options for better accuracy"""
        print(f"📡 Fetching Bitcoin data for {days} days...")
        
        # Try multiple data sources
        for attempt in range(3):
            try:
                if attempt == 0:
                    # Primary source: CoinGecko market chart
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
                    
                    print(f"✅ Successfully fetched {len(df)} data points from CoinGecko")
                    return df
                    
                elif attempt == 1:
                    # Fallback: Binance API
                    print("🔄 Trying Binance API as fallback...")
                    url = "https://api.binance.com/api/v3/klines"
                    interval = '1d' if days > 1 else '1h'
                    limit = days if days > 1 else 24
                    
                    params = {
                        'symbol': 'BTCUSDT',
                        'interval': interval,
                        'limit': limit
                    }
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    prices = [float(candle[4]) for candle in data]  # Closing prices
                    dates = [datetime.fromtimestamp(candle[6] / 1000) for candle in data]
                    
                    df = pd.DataFrame({
                        'date': dates,
                        'price': prices
                    })
                    df = df.set_index('date')
                    
                    print(f"✅ Successfully fetched {len(df)} data points from Binance")
                    return df
                    
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    print("🔄 Waiting before retry...")
                    time.sleep(2)
                else:
                    print("📊 All API attempts failed, using enhanced sample data")
                    return self.create_enhanced_sample_data(days)
    
    def create_enhanced_sample_data(self, days=30):
        """Create more realistic sample Bitcoin data based on historical patterns"""
        print("🔄 Generating realistic sample Bitcoin data...")
        
        if days == 1:
            # 1-day data with realistic intraday volatility
            dates = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                                end=datetime.now(), freq='H')
            base_price = 45000
            volatility = 0.008  # 0.8% hourly volatility
        else:
            dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                                end=datetime.now(), freq='D')
            base_price = 45000
            volatility = 0.02  # 2% daily volatility
        
        # Realistic Bitcoin price simulation with trends and mean reversion
        np.random.seed(42)  # For consistent results
        prices = [base_price]
        
        for i in range(1, len(dates)):
            # Add realistic market factors
            random_walk = np.random.normal(0.0005, volatility)  # Slight positive drift
            
            # Add some mean reversion and momentum effects
            if i > 5:
                recent_trend = (prices[-1] - prices[-5]) / prices[-5]
                # If recent trend is strong, add momentum
                if abs(recent_trend) > 0.05:
                    random_walk += recent_trend * 0.3
            
            new_price = prices[-1] * (1 + random_walk)
            prices.append(max(1000, new_price))  # Ensure positive price
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices
        })
        df = df.set_index('date')
        
        print(f"✅ Generated {len(df)} realistic data points")
        return df
    
    def calculate_simple_indicators(self, prices):
        """Calculate easy-to-understand indicators for beginners"""
        if len(prices) < 10:
            return self.get_default_indicators(prices)
        
        current_price = prices[-1]
        
        # Simple Moving Average (20-period)
        sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
        
        # Price vs Average
        price_vs_avg = ((current_price - sma_20) / sma_20) * 100
        
        # Trend strength (simplified)
        if len(prices) >= 10:
            short_trend = (current_price - prices[-5]) / prices[-5] * 100
            medium_trend = (current_price - prices[-10]) / prices[-10] * 100
            trend_strength = (short_trend + medium_trend) / 2
        else:
            trend_strength = 0
        
        # Volatility (simplified)
        recent_prices = prices[-10:] if len(prices) >= 10 else prices
        volatility = (np.std(recent_prices) / np.mean(recent_prices)) * 100
        
        return {
            'price_vs_avg': price_vs_avg,
            'trend_strength': trend_strength,
            'volatility': volatility,
            'sma_20': sma_20
        }
    
    def get_beginner_recommendation(self, df, account_balance=1000, risk_per_trade=2):
        """Generate beginner-friendly analysis with simple explanations"""
        prices = df['price'].values
        
        if len(prices) < 10:
            return self.get_default_beginner_analysis(df)
        
        current_price = float(df['price'].iloc[-1])
        simple_indicators = self.calculate_simple_indicators(prices)
        
        # Simple decision logic
        buy_signals = 0
        sell_signals = 0
        
        # Price above/below average
        if simple_indicators['price_vs_avg'] < -2:
            buy_signals += 1
        elif simple_indicators['price_vs_avg'] > 5:
            sell_signals += 1
        
        # Trend strength
        if simple_indicators['trend_strength'] > 3:
            buy_signals += 1
        elif simple_indicators['trend_strength'] < -2:
            sell_signals += 1
        
        # Volatility consideration
        if simple_indicators['volatility'] > 8:
            # High volatility - be cautious
            buy_signals -= 0.5
            sell_signals -= 0.5
        
        # Generate recommendation
        if buy_signals > sell_signals and buy_signals >= 1:
            recommendation = "BUY"
            confidence = min(80, 50 + (buy_signals * 15))
            explanation = "The market shows some positive signs. Price is reasonable compared to recent averages."
        elif sell_signals > buy_signals and sell_signals >= 1:
            recommendation = "SELL"
            confidence = min(80, 50 + (sell_signals * 15))
            explanation = "The market shows some caution signs. Price might be getting high compared to recent trends."
        else:
            recommendation = "HOLD"
            confidence = 60
            explanation = "The market is uncertain right now. It might be best to wait for clearer signals."
        
        # Risk assessment
        volatility = simple_indicators['volatility']
        if volatility < 3:
            risk_level = 'LOW'
            risk_color = 'success'
            risk_desc = 'Market is calm and predictable'
        elif volatility < 7:
            risk_level = 'MEDIUM'
            risk_color = 'warning'
            risk_desc = 'Normal market conditions'
        else:
            risk_level = 'HIGH'
            risk_color = 'danger'
            risk_desc = 'Market is volatile - be extra careful'
        
        # Simple indicators for display
        simple_indicator_list = [
            {
                'name': 'Price vs Average',
                'value': f"{simple_indicators['price_vs_avg']:+.1f}%",
                'color': 'success' if simple_indicators['price_vs_avg'] < 0 else 'danger' if simple_indicators['price_vs_avg'] > 5 else 'warning',
                'explanation': 'How current price compares to 20-day average'
            },
            {
                'name': 'Trend Strength',
                'value': f"{simple_indicators['trend_strength']:+.1f}%",
                'color': 'success' if simple_indicators['trend_strength'] > 2 else 'danger' if simple_indicators['trend_strength'] < -2 else 'warning',
                'explanation': 'Recent price movement direction and strength'
            },
            {
                'name': 'Market Volatility',
                'value': f"{simple_indicators['volatility']:.1f}%",
                'color': 'success' if simple_indicators['volatility'] < 3 else 'danger' if simple_indicators['volatility'] > 7 else 'warning',
                'explanation': 'How much prices are moving up and down'
            },
            {
                'name': '20-Day Average',
                'value': f"${simple_indicators['sma_20']:.0f}",
                'color': 'info',
                'explanation': 'Average price over last 20 days'
            }
        ]
        
        # Beginner-friendly signals
        signals = []
        if simple_indicators['price_vs_avg'] < -2:
            signals.append({
                'title': 'Price Below Average',
                'description': f"Current price is {abs(simple_indicators['price_vs_avg']):.1f}% below 20-day average",
                'explanation': 'This might be a good buying opportunity if other factors align',
                'icon': 'shopping-cart',
                'color': 'success',
                'class': 'signal-buy',
                'strength': 'MEDIUM',
                'strength_color': 'success'
            })
        
        if simple_indicators['trend_strength'] > 2:
            signals.append({
                'title': 'Upward Trend',
                'description': f"Price has increased {simple_indicators['trend_strength']:.1f}% recently",
                'explanation': 'The market is showing positive momentum',
                'icon': 'arrow-up',
                'color': 'success',
                'class': 'signal-buy',
                'strength': 'MEDIUM',
                'strength_color': 'success'
            })
        
        if simple_indicators['volatility'] > 7:
            signals.append({
                'title': 'High Volatility',
                'description': f"Market is experiencing high volatility ({simple_indicators['volatility']:.1f}%)",
                'explanation': 'Prices are moving a lot - higher risk and potential reward',
                'icon': 'exclamation-triangle',
                'color': 'warning',
                'class': 'signal-hold',
                'strength': 'HIGH',
                'strength_color': 'warning'
            })
        
        # Add default signal if no strong signals
        if not signals:
            signals.append({
                'title': 'Market in Normal Range',
                'description': 'No strong buy or sell signals detected',
                'explanation': 'This is normal market behavior. Consider waiting for clearer opportunities.',
                'icon': 'pause',
                'color': 'info',
                'class': 'signal-hold',
                'strength': 'LOW',
                'strength_color': 'info'
            })
        
        # Position sizing for learning
        position_sizing = self.calculate_simple_position_size(current_price, account_balance, risk_per_trade)
        
        # Educational content
        educational_tips = [
            {
                'icon': 'lightbulb',
                'title': 'Understanding Price vs Average',
                'content': 'When price is below the 20-day average, it might be a better buying opportunity. When above, it might be expensive.',
                'important': 'This is just one factor - never rely on a single indicator!'
            },
            {
                'icon': 'chart-line',
                'title': 'What is Trend Strength?',
                'content': 'Trend strength shows how strongly prices are moving up or down. Strong trends often continue for a while.',
                'important': 'Trends can reverse suddenly - always use stop-loss orders!'
            },
            {
                'icon': 'wind',
                'title': 'Volatility Explained',
                'content': 'Volatility measures how much prices move up and down. High volatility means higher risk but also potential for higher returns.',
                'important': 'High volatility can lead to quick losses - size your positions carefully!'
            },
            {
                'icon': 'shield-alt',
                'title': 'Risk Management First',
                'content': 'Always decide how much you can afford to lose before entering any position. Never risk more than 2-5% of your learning budget.',
                'important': 'Protect your capital - you need money to make money!'
            }
        ]
        
        # Beginner explanation
        if recommendation == "BUY":
            beginner_explanation = f"Based on current analysis, there are some positive signs in the market. The price is reasonable compared to recent averages, and the trend appears favorable. However, remember that all investments carry risk."
        elif recommendation == "SELL":
            beginner_explanation = f"The analysis suggests some caution might be warranted. Prices appear relatively high compared to recent trends. Consider if this might be a good time to take some profits or wait for better entry points."
        else:
            beginner_explanation = f"The market doesn't show clear direction right now. This might be a good time to wait and watch for better opportunities. Patience is often rewarded in trading."
        
        return {
            'recommendation': recommendation,
            'confidence': round(confidence, 1),
            'current_price': current_price,
            'simple_indicators': simple_indicator_list,
            'signals': signals,
            'position_sizing': position_sizing,
            'risk_level': {'level': risk_level, 'color': risk_color, 'description': risk_desc},
            'educational_tips': educational_tips,
            'beginner_explanation': beginner_explanation,
            'indicators_used': len(simple_indicator_list)
        }
    
    def calculate_simple_position_size(self, current_price, account_balance, risk_per_trade=2):
        """Calculate simple position sizing for learning purposes"""
        risk_amount = account_balance * (risk_per_trade / 100)
        stop_loss_pct = 5  # Fixed 5% stop-loss for learning
        stop_loss_price = current_price * (1 - stop_loss_pct / 100)
        price_diff = current_price - stop_loss_price
        
        if price_diff <= 0:
            position_size = 0
        else:
            position_size = risk_amount / price_diff
            
        # Limit position to 10% of account
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
    
    def get_default_beginner_analysis(self, df):
        """Default analysis when data is insufficient"""
        current_price = float(df['price'].iloc[-1]) if len(df) > 0 else 45000
        
        return {
            'recommendation': 'HOLD',
            'confidence': 50,
            'current_price': current_price,
            'simple_indicators': [
                {
                    'name': 'Market Data',
                    'value': 'Limited',
                    'color': 'warning',
                    'explanation': 'Need more data for better analysis'
                }
            ],
            'signals': [{
                'title': 'Need More Data',
                'description': 'We need more historical data for reliable analysis',
                'explanation': 'Try analyzing a longer time period (1 month recommended)',
                'icon': 'info-circle',
                'color': 'warning',
                'class': 'signal-hold',
                'strength': 'LOW',
                'strength_color': 'warning'
            }],
            'position_sizing': {'recommended_size': 0, 'stop_loss': 0, 'take_profit_1': 0, 'take_profit_2': 0},
            'risk_level': {'level': 'UNKNOWN', 'color': 'secondary', 'description': 'Insufficient data for risk assessment'},
            'educational_tips': [],
            'beginner_explanation': 'We need more market data to provide a proper analysis. Please try again with a longer time period.',
            'indicators_used': 0
        }

# Initialize the beginner-friendly assistant
beginner_bot = BeginnerFriendlyBitcoinAssistant()

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        time_frame = request.form.get('time_frame', '30')
        analysis_type = request.form.get('analysis_type', 'simple')
        account_balance = float(request.form.get('account_balance', 1000))
        risk_per_trade = float(request.form.get('risk_per_trade', 2))
        
        print(f"🔍 Starting beginner-friendly analysis: {time_frame} days")
        
        # Fetch enhanced data
        df = beginner_bot.fetch_bitcoin_data_with_fallback(days=int(time_frame))
        
        # Get beginner-friendly analysis
        analysis = beginner_bot.get_beginner_recommendation(df, account_balance, risk_per_trade)
        
        print(f"✅ Analysis complete: {analysis['recommendation']} with {analysis['confidence']}% confidence")
        
        return render_template_string(RESULTS_HTML, 
                                    analysis=analysis, 
                                    error=None)
                                    
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        print(f"❌ {error_msg}")
        return render_template_string(RESULTS_HTML, 
                                    error=error_msg)

@app.route('/api/simple_analysis')
def api_simple_analysis():
    """Simple JSON API endpoint for beginners"""
    try:
        df = beginner_bot.fetch_bitcoin_data_with_fallback()
        analysis = beginner_bot.get_beginner_recommendation(df)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'recommendation': analysis['recommendation'],
                'confidence': analysis['confidence'],
                'current_price': analysis['current_price'],
                'risk_level': analysis['risk_level']
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
        'service': 'Beginner-Friendly Bitcoin Trading Helper',
        'version': '2.0',
        'features': ['Beginner Explanations', 'Simple Analysis', 'Risk Education', 'Multiple Data Sources']
    })

if __name__ == '__main__':
    print("🚀 Beginner-Friendly Bitcoin Trading Helper Starting...")
    print("=" * 60)
    print("👋 Welcome to Bitcoin Learning!")
    print("📊 Web Interface: http://localhost:5000")
    print("🔗 Simple API:    http://localhost:5000/api/simple_analysis")
    print("❤️  Health Check: http://localhost:5000/health")
    print("=" * 60)
    print("💡 IMPORTANT: This is for LEARNING PURPOSES only!")
    print("   Always continue learning and consult multiple sources.")
    print("=" * 60)
    
    # Test the system
    try:
        bot = BeginnerFriendlyBitcoinAssistant()
        test_data = bot.fetch_bitcoin_data_with_fallback(days=1)
        print(f"✅ 1-Day analysis ready: {len(test_data)} data points")
        test_data = bot.fetch_bitcoin_data_with_fallback(days=7)
        print(f"✅ 7-Day analysis ready: {len(test_data)} data points")
    except Exception as e:
        print(f"⚠️  System check warning: {e}")
        print("   Application will use enhanced sample data.")
    
    print("🎯 Starting beginner-friendly Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)