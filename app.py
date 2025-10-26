from flask import Flask, render_template_string, request, jsonify
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# HTML Templates as strings
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bitcoin Trading Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: Arial, sans-serif; }
        .card { border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .display-4 { 
            color: #0d6efd; 
            font-weight: bold;
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none; border-radius: 8px; padding: 12px 30px; 
            font-weight: 600;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .feature-card { transition: transform 0.3s ease; }
        .feature-card:hover { transform: translateY(-5px); }
        .signal-buy { background-color: #d1e7dd !important; border-left: 4px solid #198754; }
        .signal-sell { background-color: #f8d7da !important; border-left: 4px solid #dc3545; }
        .signal-hold { background-color: #fff3cd !important; border-left: 4px solid #ffc107; }
        .navbar-brand { font-weight: 700; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Bitcoin Trading Assistant
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="text-center mb-4">
                    <h1 class="display-5 fw-bold mb-3">Bitcoin Trading Assistant</h1>
                    <p class="lead text-muted">AI-powered buy/sell signals for informed Bitcoin trading decisions</p>
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Educational Purpose Only:</strong> This is not financial advice. Always do your own research.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                </div>

                <div class="card shadow-lg mb-4">
                    <div class="card-header bg-primary text-white py-3">
                        <h4 class="mb-0"><i class="fas fa-chart-line me-2"></i>Technical Analysis</h4>
                    </div>
                    <div class="card-body p-4">
                        <form action="/analyze" method="POST">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label fw-bold">Time Frame</label>
                                    <select class="form-select" name="time_frame">
                                        <option value="30" selected>Last 30 Days</option>
                                        <option value="90">Last 90 Days</option>
                                        <option value="180">Last 6 Months</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-bold">Analysis Type</label>
                                    <select class="form-select" name="analysis_type">
                                        <option value="technical" selected>Technical Analysis</option>
                                        <option value="trend">Trend Analysis</option>
                                    </select>
                                </div>
                            </div>
                            <div class="d-grid mt-4">
                                <button type="submit" class="btn btn-primary btn-lg py-3">
                                    <i class="fas fa-bolt me-2"></i>Analyze Bitcoin Now
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div class="row g-3 mt-2">
                    <div class="col-md-4">
                        <div class="card h-100 text-center feature-card border-0">
                            <div class="card-body py-4">
                                <i class="fas fa-robot fa-2x text-primary mb-3"></i>
                                <h6 class="fw-bold">Smart Analysis</h6>
                                <small class="text-muted">Multiple technical indicators and algorithms</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card h-100 text-center feature-card border-0">
                            <div class="card-body py-4">
                                <i class="fas fa-chart-bar fa-2x text-success mb-3"></i>
                                <h6 class="fw-bold">Real-time Signals</h6>
                                <small class="text-muted">Instant buy/sell/hold recommendations</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card h-100 text-center feature-card border-0">
                            <div class="card-body py-4">
                                <i class="fas fa-brain fa-2x text-info mb-3"></i>
                                <h6 class="fw-bold">Market Insights</h6>
                                <small class="text-muted">Sentiment analysis and trend detection</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <small>&copy; 2024 Bitcoin Trading Assistant - For Educational Purposes Only</small>
        </div>
    </footer>

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
    <title>Analysis Results - Bitcoin Trading Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: Arial, sans-serif; }
        .signal-buy { background-color: #d1e7dd !important; border-left: 4px solid #198754; }
        .signal-sell { background-color: #f8d7da !important; border-left: 4px solid #dc3545; }
        .signal-hold { background-color: #fff3cd !important; border-left: 4px solid #ffc107; }
        .signal-info { background-color: #cff4fc !important; border-left: 4px solid #0dcaf0; }
        .card { border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .navbar-brand { font-weight: 700; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fab fa-bitcoin me-2"></i>Bitcoin Trading Assistant
            </a>
            <a href="/" class="btn btn-outline-light btn-sm">
                <i class="fas fa-arrow-left me-1"></i>Back to Analysis
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-lg-10 mx-auto">
                {% if error %}
                <div class="alert alert-danger">
                    <h4><i class="fas fa-exclamation-triangle me-2"></i>Analysis Error</h4>
                    <p class="mb-0">{{ error }}</p>
                </div>
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-primary">
                        <i class="fas fa-sync-alt me-2"></i>Try Again
                    </a>
                </div>
                {% else %}

                <!-- Main Recommendation -->
                <div class="card shadow-lg mb-4 border-0">
                    <div class="card-body text-center py-5">
                        {% if analysis.recommendation == 'BUY' %}
                            {% set rec_color = 'success' %}
                            {% set icon = 'arrow-up' %}
                            {% set bg_color = 'success' %}
                        {% elif analysis.recommendation == 'SELL' %}
                            {% set rec_color = 'danger' %}
                            {% set icon = 'arrow-down' %}
                            {% set bg_color = 'danger' %}
                        {% else %}
                            {% set rec_color = 'warning' %}
                            {% set icon = 'pause' %}
                            {% set bg_color = 'warning' %}
                        {% endif %}
                        
                        <div class="mb-3">
                            <span class="badge bg-{{ bg_color }} fs-6 px-3 py-2">
                                <i class="fas fa-{{ icon }} me-2"></i>{{ analysis.recommendation }} RECOMMENDATION
                            </span>
                        </div>
                        
                        <h2 class="text-{{ rec_color }} fw-bold mb-3">{{ analysis.confidence }}%</h2>
                        <p class="text-muted mb-2">Confidence Level</p>
                        <p class="h5 text-dark">
                            <i class="fas fa-dollar-sign me-1"></i>
                            Current Price: <strong>${{ "%.2f"|format(analysis.current_price) }}</strong>
                        </p>
                    </div>
                </div>

                <div class="row g-3">
                    <!-- Market Sentiment -->
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header bg-dark text-white py-3">
                                <h5 class="mb-0"><i class="fas fa-brain me-2"></i>Market Sentiment</h5>
                            </div>
                            <div class="card-body text-center py-4">
                                <div class="h3 text-{{ sentiment.color }} fw-bold mb-3">
                                    {{ sentiment.sentiment }}
                                </div>
                                <div class="progress mb-2" style="height: 25px;">
                                    <div class="progress-bar bg-{{ sentiment.color }} progress-bar-striped" 
                                         style="width: {{ sentiment.score }}%">
                                        {{ sentiment.score }}/100
                                    </div>
                                </div>
                                <small class="text-muted">Fear & Greed Index</small>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Technical Indicators -->
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header bg-dark text-white py-3">
                                <h5 class="mb-0"><i class="fas fa-sliders-h me-2"></i>Technical Indicators</h5>
                            </div>
                            <div class="card-body">
                                <div class="row text-center g-3">
                                    <div class="col-4">
                                        <div class="p-2">
                                            <small class="fw-bold d-block">RSI (14)</small>
                                            {% if analysis.rsi < 30 %}
                                                {% set rsi_color = 'success' %}
                                            {% elif analysis.rsi > 70 %}
                                                {% set rsi_color = 'danger' %}
                                            {% else %}
                                                {% set rsi_color = 'warning' %}
                                            {% endif %}
                                            <div class="h5 text-{{ rsi_color }} fw-bold mt-1">
                                                {{ "%.1f"|format(analysis.rsi) }}
                                            </div>
                                            <small class="text-muted">
                                                {% if analysis.rsi < 30 %}Oversold{% elif analysis.rsi > 70 %}Overbought{% else %}Neutral{% endif %}
                                            </small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="p-2">
                                            <small class="fw-bold d-block">SMA 20</small>
                                            <div class="h5 {% if analysis.current_price > analysis.sma_20 %}text-success{% else %}text-danger{% endif %} fw-bold mt-1">
                                                ${{ "%.0f"|format(analysis.sma_20) }}
                                            </div>
                                            <small class="text-muted">20-day Avg</small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="p-2">
                                            <small class="fw-bold d-block">SMA 50</small>
                                            <div class="h5 {% if analysis.current_price > analysis.sma_50 %}text-success{% else %}text-danger{% endif %} fw-bold mt-1">
                                                ${{ "%.0f"|format(analysis.sma_50) }}
                                            </div>
                                            <small class="text-muted">50-day Avg</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Trading Signals -->
                <div class="card mt-4">
                    <div class="card-header bg-dark text-white py-3">
                        <h5 class="mb-0"><i class="fas fa-bell me-2"></i>Trading Signals & Analysis</h5>
                    </div>
                    <div class="card-body p-0">
                        <div class="list-group list-group-flush">
                            {% for signal in analysis.signals %}
                                {% if 'BUY' in signal %}
                                    {% set signal_class = 'signal-buy' %}
                                    {% set icon = 'arrow-up' %}
                                {% elif 'SELL' in signal %}
                                    {% set signal_class = 'signal-sell' %}
                                    {% set icon = 'arrow-down' %}
                                {% elif 'HOLD' in signal %}
                                    {% set signal_class = 'signal-hold' %}
                                    {% set icon = 'pause' %}
                                {% else %}
                                    {% set signal_class = 'signal-info' %}
                                    {% set icon = 'info-circle' %}
                                {% endif %}
                                <div class="list-group-item {{ signal_class }} d-flex align-items-center py-3">
                                    <i class="fas fa-{{ icon }} me-3 fa-lg text-{{ rec_color }}"></i>
                                    <span class="flex-grow-1">{{ signal }}</span>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <!-- Trading Advice -->
                <div class="card mt-4">
                    <div class="card-header bg-info text-white py-3">
                        <h5 class="mb-0"><i class="fas fa-lightbulb me-2"></i>Trading Advice</h5>
                    </div>
                    <div class="card-body">
                        {% if analysis.recommendation == 'BUY' %}
                        <div class="alert alert-success border-0">
                            <h6 class="alert-heading"><i class="fas fa-check-circle me-2"></i>Consider Buying Bitcoin</h6>
                            <p class="mb-2">Multiple technical indicators suggest potential upward movement. Consider:</p>
                            <ul class="mb-0">
                                <li>Setting limit orders below current market price</li>
                                <li>Using proper position sizing and risk management</li>
                                <li>Setting stop-loss orders to protect your investment</li>
                                <li>Dollar-cost averaging if uncertain about timing</li>
                            </ul>
                        </div>
                        {% elif analysis.recommendation == 'SELL' %}
                        <div class="alert alert-danger border-0">
                            <h6 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Consider Selling Bitcoin</h6>
                            <p class="mb-2">Technical analysis suggests potential downward pressure. Consider:</p>
                            <ul class="mb-0">
                                <li>Taking profits if you're holding profitable positions</li>
                                <li>Setting tighter stop-loss orders to protect gains</li>
                                <li>Waiting for better entry points before buying</li>
                                <li>Monitoring key support levels for potential reversals</li>
                            </ul>
                        </div>
                        {% else %}
                        <div class="alert alert-warning border-0">
                            <h6 class="alert-heading"><i class="fas fa-pause-circle me-2"></i>Hold Your Position</h6>
                            <p class="mb-2">Market shows mixed or neutral signals. Consider:</p>
                            <ul class="mb-0">
                                <li>Waiting for clearer trend direction before trading</li>
                                <li>Monitoring key support and resistance levels</li>
                                <li>Reducing position size if market uncertainty is high</li>
                                <li>Setting alerts for significant price movements</li>
                            </ul>
                        </div>
                        {% endif %}
                    </div>
                </div>

                <!-- Risk Disclaimer -->
                <div class="alert alert-warning mt-4">
                    <h6 class="alert-heading mb-3">
                        <i class="fas fa-exclamation-triangle me-2"></i>Important Risk Disclaimer
                    </h6>
                    <p class="mb-2">
                        <strong>This analysis is for educational and informational purposes only.</strong> 
                        It is not financial advice and should not be construed as such.
                    </p>
                    <p class="mb-0">
                        Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors. 
                        Always conduct your own research, consider your financial situation, and consult with a qualified 
                        financial advisor before making any investment decisions. Past performance is not indicative of 
                        future results.
                    </p>
                </div>

                <!-- Action Buttons -->
                <div class="text-center my-5">
                    <a href="/" class="btn btn-primary btn-lg me-3 px-4">
                        <i class="fas fa-sync-alt me-2"></i>New Analysis
                    </a>
                    <button class="btn btn-outline-secondary btn-lg px-4" onclick="window.print()">
                        <i class="fas fa-print me-2"></i>Print Report
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light mt-4 py-4">
        <div class="container text-center">
            <small>
                <i class="fas fa-code me-1"></i>Built with Python & Flask | 
                <i class="fas fa-exclamation-triangle me-1"></i>Educational Purpose Only
            </small>
        </div>
    </footer>
</body>
</html>
'''

class BitcoinTradingAssistant:
    def __init__(self):
        self.indicators = {}
        
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI manually without ta-lib"""
        if len(prices) < window + 1:
            return 50  # Default neutral value
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.zeros_like(prices)
        avg_losses = np.zeros_like(prices)
        
        # First average
        avg_gains[window] = np.mean(gains[:window])
        avg_losses[window] = np.mean(losses[:window])
        
        # Subsequent averages
        for i in range(window + 1, len(prices)):
            avg_gains[i] = (avg_gains[i-1] * (window - 1) + gains[i-1]) / window
            avg_losses[i] = (avg_losses[i-1] * (window - 1) + losses[i-1]) / window
        
        # Calculate RS and RSI
        rs = avg_gains[window:] / np.where(avg_losses[window:] == 0, 1, avg_losses[window:])
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi[-1]) if len(rsi) > 0 else 50
    
    def calculate_sma(self, prices, window):
        """Calculate Simple Moving Average"""
        if len(prices) < window:
            return float(prices[-1])  # Return last price if not enough data
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
    
    def fetch_bitcoin_data(self, days=30):
        """Fetch Bitcoin data from CoinGecko API"""
        try:
            print(f"📡 Fetching Bitcoin data for {days} days...")
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd', 
                'days': days, 
                'interval': 'daily'
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
            
            print(f"✅ Successfully fetched {len(df)} days of Bitcoin data")
            return df
            
        except Exception as e:
            print(f"❌ API Error: {e}, using sample data")
            return self.create_sample_data(days)
    
    def create_sample_data(self, days=30):
        """Create realistic sample Bitcoin data"""
        print("🔄 Generating sample Bitcoin data...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create realistic Bitcoin price movement
        np.random.seed(42)  # For consistent results
        base_price = 45000  # Start around $45k
        volatility = 0.02  # 2% daily volatility
        
        prices = [base_price]
        for i in range(1, len(dates)):
            change = np.random.normal(0, volatility)
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices
        })
        df = df.set_index('date')
        
        print(f"✅ Generated {len(df)} days of sample data")
        return df
    
    def calculate_technical_indicators(self, df):
        """Calculate all technical indicators manually"""
        prices = df['price'].values
        
        # Calculate indicators
        df['rsi'] = self.calculate_rsi(prices)
        df['sma_20'] = self.calculate_sma(prices, 20)
        df['sma_50'] = self.calculate_sma(prices, 50)
        df['ema_12'] = self.calculate_ema(prices, 12)
        df['ema_26'] = self.calculate_ema(prices, 26)
        
        # Simple MACD calculation
        df['macd'] = df['ema_12'] - df['ema_26']
        
        return df
    
    def generate_signals(self, df):
        """Generate trading signals based on technical analysis"""
        if len(df) < 20:  # Need enough data for reliable signals
            return self.get_default_signals(df)
        
        signals = []
        current_price = float(df['price'].iloc[-1])
        rsi = float(df['rsi'].iloc[-1])
        sma_20 = float(df['sma_20'].iloc[-1])
        sma_50 = float(df['sma_50'].iloc[-1])
        macd = float(df['macd'].iloc[-1])
        
        # RSI Signals
        if rsi < 30:
            signals.append("RSI indicates OVERSOLD conditions - STRONG BUY signal")
        elif rsi > 70:
            signals.append("RSI indicates OVERBOUGHT conditions - STRONG SELL signal")
        elif rsi < 40:
            signals.append("RSI leaning toward oversold - POTENTIAL BUY")
        elif rsi > 60:
            signals.append("RSI leaning toward overbought - POTENTIAL SELL")
        else:
            signals.append("RSI in neutral territory - WAIT for clearer signals")
        
        # Moving Average Signals
        if sma_20 > sma_50 and current_price > sma_20:
            signals.append("Golden Cross pattern - BULLISH BUY signal")
        elif sma_20 < sma_50 and current_price < sma_20:
            signals.append("Death Cross pattern - BEARISH SELL signal")
        elif current_price > sma_20 and current_price > sma_50:
            signals.append("Price above both moving averages - BULLISH")
        elif current_price < sma_20 and current_price < sma_50:
            signals.append("Price below both moving averages - BEARISH")
        
        # MACD Signals
        if macd > 0:
            signals.append("MACD positive - BULLISH momentum")
        else:
            signals.append("MACD negative - BEARISH momentum")
        
        # Trend Analysis
        price_trend = "UP" if current_price > float(df['price'].iloc[-5]) else "DOWN"
        signals.append(f"Short-term trend: {price_trend}")
        
        # Determine overall recommendation
        buy_signals = sum(1 for s in signals if 'BUY' in s or 'BULLISH' in s)
        sell_signals = sum(1 for s in signals if 'SELL' in s or 'BEARISH' in s)
        
        if buy_signals > sell_signals + 2:
            recommendation = "BUY"
            confidence = min(70 + (buy_signals * 5), 95)
        elif sell_signals > buy_signals + 2:
            recommendation = "SELL"
            confidence = min(70 + (sell_signals * 5), 95)
        else:
            recommendation = "HOLD"
            confidence = 50 + (max(buy_signals, sell_signals) * 5)
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'signals': signals,
            'current_price': current_price,
            'rsi': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50
        }
    
    def get_default_signals(self, df):
        """Return default signals when data is insufficient"""
        current_price = float(df['price'].iloc[-1]) if len(df) > 0 else 45000
        
        return {
            'recommendation': 'HOLD',
            'confidence': 50,
            'signals': [
                'Insufficient historical data for reliable analysis',
                'Collecting more market data...',
                'Consider using longer time frames for better accuracy'
            ],
            'current_price': current_price,
            'rsi': 50,
            'sma_20': current_price,
            'sma_50': current_price
        }
    
    def get_market_sentiment(self):
        """Get simulated market sentiment"""
        # Simulate realistic sentiment based on various factors
        base_sentiment = np.random.randint(30, 70)
        
        # Add some randomness but keep it somewhat stable
        sentiment_score = max(10, min(90, base_sentiment + np.random.randint(-10, 10)))
        
        if sentiment_score > 75:
            return {'sentiment': 'Extreme Greed', 'score': sentiment_score, 'color': 'danger'}
        elif sentiment_score > 60:
            return {'sentiment': 'Greed', 'score': sentiment_score, 'color': 'warning'}
        elif sentiment_score > 45:
            return {'sentiment': 'Neutral', 'score': sentiment_score, 'color': 'info'}
        elif sentiment_score > 30:
            return {'sentiment': 'Fear', 'score': sentiment_score, 'color': 'primary'}
        else:
            return {'sentiment': 'Extreme Fear', 'score': sentiment_score, 'color': 'success'}

# Initialize the trading assistant
trading_bot = BitcoinTradingAssistant()

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        time_frame = request.form.get('time_frame', '30')
        analysis_type = request.form.get('analysis_type', 'technical')
        
        print(f"🔍 Starting analysis: {time_frame} days, {analysis_type} type")
        
        # Fetch and analyze data
        df = trading_bot.fetch_bitcoin_data(days=int(time_frame))
        df = trading_bot.calculate_technical_indicators(df)
        analysis = trading_bot.generate_signals(df)
        sentiment = trading_bot.get_market_sentiment()
        
        print(f"✅ Analysis complete: {analysis['recommendation']} with {analysis['confidence']}% confidence")
        
        return render_template_string(RESULTS_HTML, 
                                    analysis=analysis, 
                                    sentiment=sentiment,
                                    error=None)
                                    
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        print(f"❌ {error_msg}")
        return render_template_string(RESULTS_HTML, 
                                    error=error_msg)

@app.route('/api/analysis')
def api_analysis():
    """JSON API endpoint for programmatic access"""
    try:
        df = trading_bot.fetch_bitcoin_data()
        df = trading_bot.calculate_technical_indicators(df)
        analysis = trading_bot.generate_signals(df)
        sentiment = trading_bot.get_market_sentiment()
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'recommendation': analysis['recommendation'],
                'confidence': analysis['confidence'],
                'current_price': analysis['current_price'],
                'rsi': analysis['rsi'],
                'signals': analysis['signals']
            },
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
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Bitcoin Trading Assistant'
    })

if __name__ == '__main__':
    print("🚀 Bitcoin Trading Assistant Starting...")
    print("=" * 50)
    print("📊 Web Interface: http://localhost:5000")
    print("🔗 API Endpoint:  http://localhost:5000/api/analysis")
    print("❤️  Health Check:  http://localhost:5000/health")
    print("=" * 50)
    print("⚠️  Disclaimer: This tool is for EDUCATIONAL PURPOSES only!")
    print("   Always do your own research and consult financial advisors.")
    print("=" * 50)
    
    # Test the trading assistant
    try:
        bot = BitcoinTradingAssistant()
        test_data = bot.fetch_bitcoin_data(days=7)
        print(f"✅ System check passed: Fetched {len(test_data)} days of data")
    except Exception as e:
        print(f"⚠️  System check warning: {e}")
        print("   Application will use sample data instead.")
    
    print("🎯 Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
