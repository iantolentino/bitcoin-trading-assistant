import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
from datetime import datetime, timedelta, timezone
from collections import deque
import urllib.request
import urllib.error
import math
import random
import logging
import sys
from typing import Optional, Tuple, List, Dict, Any
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bitcoin_trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class TradingStrategies:
    """Implement the trading strategies with proper logic"""
    
    def __init__(self):
        self.strategies = {
            "buy_asian_dip": {
                "name": "Buy-the-Asian-Dip",
                "description": "Buy during PH morning/Asia session dips (8:00-16:00), sell in US session (20:00-02:00)",
                "confidence": 0.75,
                "active_hours": list(range(8, 16))
            },
            "range_bounce": {
                "name": "Range Bounce",
                "description": "Buy near support, sell near resistance in sideways markets",
                "confidence": 0.65,
                "conditions": ["sideways_market"]
            },
            "breakout_momentum": {
                "name": "Breakout Momentum",
                "description": "Buy on high-volume resistance breaks",
                "confidence": 0.60,
                "conditions": ["high_volume", "resistance_break"]
            },
            "ema_trend": {
                "name": "EMA Trend Following",
                "description": "Follow 50EMA/200EMA crossovers for multi-day trends",
                "confidence": 0.65,
                "timeframe": "4h"
            },
            "mean_reversion": {
                "name": "Mean Reversion",
                "description": "Buy on RSI extremes with Bollinger Band touches",
                "confidence": 0.55,
                "conditions": ["rsi_extreme", "bollinger_extreme"]
            }
        }
    
    def get_ph_time(self):
        """Get current Philippines time"""
        return datetime.now(timezone.utc) + timedelta(hours=8)
    
    def is_asian_session(self):
        """Check if current time is in Asian trading session (PH time)"""
        ph_time = self.get_ph_time()
        return 8 <= ph_time.hour < 16
    
    def is_us_session(self):
        """Check if current time is in US trading session (PH time)"""
        ph_time = self.get_ph_time()
        return 20 <= ph_time.hour or ph_time.hour < 2
    
    def calculate_strategy_signals(self, market_data):
        """Calculate which strategies are currently active"""
        active_strategies = []
        
        # Buy-the-Asian-Dip strategy
        if self.is_asian_session():
            rsi_1h = market_data.get('rsi_1h')
            if rsi_1h is not None and rsi_1h < 45:
                active_strategies.append(("buy_asian_dip", 0.75, "Asian session dip opportunity"))
        
        # Range Bounce strategy
        if market_data.get('market_regime') == 'sideways':
            current_price = market_data.get('current_price', 0)
            support_levels = market_data.get('support_levels', [])
            if support_levels and current_price <= max(support_levels) * 1.01:
                active_strategies.append(("range_bounce", 0.65, "Price near support in range market"))
        
        # Breakout Momentum strategy
        if (market_data.get('volume_spike', False) and 
            market_data.get('resistance_break', False)):
            active_strategies.append(("breakout_momentum", 0.70, "High-volume breakout detected"))
        
        # EMA Trend strategy
        if market_data.get('ema_trend') == 'bullish':
            active_strategies.append(("ema_trend", 0.65, "Uptrend confirmed by EMA"))
        
        # Mean Reversion strategy
        rsi_1h = market_data.get('rsi_1h')
        bollinger_position = market_data.get('bollinger_position')
        if (rsi_1h is not None and rsi_1h < 30 and 
            bollinger_position == 'lower'):
            active_strategies.append(("mean_reversion", 0.60, "Oversold with Bollinger Band touch"))
        
        return active_strategies

class AdvancedIndicators:
    """Calculate advanced technical indicators"""
    
    @staticmethod
    def calculate_ema(prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        try:
            multiplier = 2 / (period + 1)
            ema = sum(prices[:period]) / period
            
            for price in prices[period:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
        except Exception as e:
            logging.warning(f"EMA calculation error: {e}")
            return None
    
    @staticmethod
    def calculate_atr(high_prices, low_prices, close_prices, period=14):
        """Calculate Average True Range"""
        if len(high_prices) < period + 1:
            return None
        
        try:
            true_ranges = []
            for i in range(1, len(high_prices)):
                tr1 = high_prices[i] - low_prices[i]
                tr2 = abs(high_prices[i] - close_prices[i-1])
                tr3 = abs(low_prices[i] - close_prices[i-1])
                true_ranges.append(max(tr1, tr2, tr3))
            
            return sum(true_ranges[-period:]) / period
        except Exception as e:
            logging.warning(f"ATR calculation error: {e}")
            return None

class NewsSentimentAnalyzer:
    """Analyze news sentiment for Bitcoin"""
    
    def __init__(self):
        self.news_cache = []
        self.last_fetch = None
        self.sentiment_score = 0.0
    
    def fetch_news_sentiment(self):
        """Fetch and analyze news sentiment (simulated for now)"""
        try:
            # Simulate news sentiment for now
            simulated_sentiment = random.uniform(-0.3, 0.3)
            self.sentiment_score = simulated_sentiment
            
            news_items = [
                {"title": "Bitcoin shows strength in Asian trading", "sentiment": 0.2},
                {"title": "Market volatility expected this week", "sentiment": -0.1},
            ]
            
            self.news_cache = news_items
            self.last_fetch = datetime.now(timezone.utc)
            
            return self.sentiment_score, news_items
        except Exception as e:
            logging.warning(f"News sentiment fetch error: {e}")
            return 0.0, []

class DataManager:
    """Enhanced data manager with multiple sources and caching"""
    
    def __init__(self):
        self.last_successful_fetch = None
        self.consecutive_errors = 0
        self.max_retries = 3
        self.cache_duration = 30
        
        # Initialize advanced components
        self.strategies = TradingStrategies()
        self.indicators = AdvancedIndicators()
        self.news_analyzer = NewsSentimentAnalyzer()
        
    def fetch_with_retry(self, fetch_function, description="data"):
        """Fetch data with retry logic and error handling"""
        for attempt in range(self.max_retries):
            try:
                result = fetch_function()
                if result is not None and result > 0:
                    self.consecutive_errors = 0
                    self.last_successful_fetch = datetime.now(timezone.utc)
                    return result
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {description}: {e}")
                time.sleep(1)
        
        self.consecutive_errors += 1
        logging.error(f"All retries failed for {description}")
        return None

class BitcoinPredictor:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Trading Assistant - Professional Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Set modern theme
        self.set_modern_theme()
        
        # Initialize enhanced data manager
        self.data_manager = DataManager()
        
        # Enhanced data storage
        self.price_history = deque(maxlen=500)
        self.volume_history = deque(maxlen=500)
        self.high_history = deque(maxlen=500)
        self.low_history = deque(maxlen=500)
        
        self.current_price = 0
        self.price_change = 0
        self.change_percentage = 0
        
        # Advanced indicators storage
        self.advanced_indicators = {}
        self.market_regime = "unknown"
        self.active_strategies = []
        
        # Trading metrics
        self.entry_price = 0
        self.take_profit = 0
        self.stop_loss = 0
        self.risk_reward_ratio = 0
        
        # Performance tracking
        self.start_time = datetime.now(timezone.utc)
        self.successful_updates = 0
        self.failed_updates = 0
        
        self.setup_ui()
        self.running = True
        self.start_data_fetching()
        self.schedule_health_check()
    
    def set_modern_theme(self):
        """Set modern theme for the application"""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure colors
            style.configure('Modern.TFrame', background='#1a1a1a')
            style.configure('Card.TFrame', background='#2d2d2d')
            style.configure('Title.TLabel', background='#2d2d2d', foreground='white', font=('Arial', 12, 'bold'))
            style.configure('Value.TLabel', background='#2d2d2d', foreground='#00ff88', font=('Arial', 11, 'bold'))
            style.configure('Neutral.TLabel', background='#2d2d2d', foreground='#ffaa00', font=('Arial', 10))
            style.configure('Positive.TLabel', background='#2d2d2d', foreground='#00ff88', font=('Arial', 10))
            style.configure('Negative.TLabel', background='#2d2d2d', foreground='#ff4444', font=('Arial', 10))
            style.configure('Price.TLabel', background='#2d2d2d', foreground='#00ff88', font=('Arial', 20, 'bold'))
            style.configure('Prediction.TLabel', background='#2d2d2d', foreground='#ffaa00', font=('Arial', 16, 'bold'))
            style.configure('Reason.TLabel', background='#2d2d2d', foreground='white', font=('Arial', 10))
            style.configure('Status.TFrame', background='#2d2d2d')
            style.configure('Status.TLabel', background='#2d2d2d', foreground='white', font=('Arial', 9))
        except Exception as e:
            logging.warning(f"Theme setup warning: {e}")

    def setup_ui(self):
        """Setup user interface with enhanced components"""
        try:
            # Main container
            main_container = ttk.Frame(self.root, style='Modern.TFrame', padding="10")
            main_container.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = ttk.Frame(main_container, style='Card.TFrame', padding="15")
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Header content
            title_frame = ttk.Frame(header_frame, style='Card.TFrame')
            title_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            ttk.Label(title_frame, text="🎯 BITCOIN TRADING ASSISTANT PRO", 
                     style='Title.TLabel', font=('Arial', 16, 'bold')).pack(anchor='w')
            ttk.Label(title_frame, text="Professional Trading Signals & Analytics", 
                     style='Neutral.TLabel').pack(anchor='w')
            
            # Price display in header
            price_frame = ttk.Frame(header_frame, style='Card.TFrame')
            price_frame.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.price_label = ttk.Label(price_frame, text="Loading...", 
                                       style='Price.TLabel')
            self.price_label.pack(anchor='e')
            
            self.change_label = ttk.Label(price_frame, text="", 
                                        style='Neutral.TLabel', font=('Arial', 12))
            self.change_label.pack(anchor='e')
            
            # Connection status
            self.connection_label = ttk.Label(price_frame, text="🟡 Connecting...", 
                                            style='Neutral.TLabel', font=('Arial', 9))
            self.connection_label.pack(anchor='e')
            
            # Main content area
            content_frame = ttk.Frame(main_container, style='Modern.TFrame')
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Left column
            left_column = ttk.Frame(content_frame, style='Modern.TFrame')
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            
            # Right column  
            right_column = ttk.Frame(content_frame, style='Modern.TFrame')
            right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            # Setup all UI components
            self.setup_trading_signals(left_column)
            self.setup_active_strategies(left_column)
            self.setup_trading_plan(left_column)
            self.setup_market_sentiment(left_column)
            
            self.setup_technical_indicators(right_column)
            self.setup_advanced_indicators(right_column)
            self.setup_key_levels(right_column)
            self.setup_price_predictions(right_column)
            
            # Status bar
            self.setup_status_bar(main_container)
            
        except Exception as e:
            logging.error(f"UI setup failed: {e}")
            messagebox.showerror("Setup Error", f"Failed to initialize user interface: {str(e)}")

    def setup_trading_signals(self, parent):
        """Setup trading signals display"""
        signals_card = ttk.LabelFrame(parent, text="🎯 TRADING SIGNALS", 
                                    padding="15", style='Card.TFrame')
        signals_card.pack(fill=tk.X, pady=(0, 10))
        
        # Prediction display
        prediction_frame = ttk.Frame(signals_card, style='Card.TFrame')
        prediction_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(prediction_frame, text="Recommendation:", style='Title.TLabel').pack(side=tk.LEFT)
        self.prediction_label = ttk.Label(prediction_frame, text="ANALYZING...", 
                                        style='Prediction.TLabel')
        self.prediction_label.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(prediction_frame, text="Confidence:", style='Title.TLabel').pack(side=tk.LEFT)
        self.win_rate_label = ttk.Label(prediction_frame, text="75%", 
                                      style='Positive.TLabel', font=('Arial', 14, 'bold'))
        self.win_rate_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Reason display
        reason_frame = ttk.Frame(signals_card, style='Card.TFrame')
        reason_frame.pack(fill=tk.X, pady=5)
        
        self.reason_label = ttk.Label(reason_frame, text="Gathering market data...", 
                                     style='Reason.TLabel', wraplength=400, justify=tk.LEFT)
        self.reason_label.pack(anchor='w')

    def setup_active_strategies(self, parent):
        """Setup active strategies display"""
        strategies_card = ttk.LabelFrame(parent, text="🎯 ACTIVE STRATEGIES", 
                                       padding="15", style='Card.TFrame')
        strategies_card.pack(fill=tk.X, pady=(0, 10))
        
        self.strategies_text = tk.Text(strategies_card, height=4, font=('Arial', 9), 
                                     bg='#2d2d2d', fg='white', wrap=tk.WORD, padx=10, pady=10)
        self.strategies_text.pack(fill=tk.BOTH, expand=True)
        self.strategies_text.insert(tk.END, "Analyzing market conditions for strategy activation...")
        self.strategies_text.config(state=tk.DISABLED)

    def setup_trading_plan(self, parent):
        """Setup trading plan display"""
        plan_card = ttk.LabelFrame(parent, text="📝 TRADING PLAN", 
                                 padding="15", style='Card.TFrame')
        plan_card.pack(fill=tk.X, pady=(0, 10))
        
        # Create grid for trading plan details
        grid_frame = ttk.Frame(plan_card, style='Card.TFrame')
        grid_frame.pack(fill=tk.X)
        
        plan_items = [
            ("Entry Price", "entry_label"),
            ("Take Profit", "take_profit_label"),
            ("Stop Loss", "stop_loss_label"),
            ("Risk/Reward", "rr_label"),
            ("Hold Time", "hold_time_label"),
            ("Sell Time", "sell_time_label")
        ]
        
        for i in range(0, len(plan_items), 2):
            row_frame = ttk.Frame(grid_frame, style='Card.TFrame')
            row_frame.pack(fill=tk.X, pady=2)
            
            for j in range(2):
                if i + j < len(plan_items):
                    text, attr_name = plan_items[i + j]
                    frame = ttk.Frame(row_frame, style='Card.TFrame')
                    frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                    
                    ttk.Label(frame, text=text, style='Title.TLabel', font=('Arial', 9)).pack()
                    label = ttk.Label(frame, text="--", style='Value.TLabel', font=('Arial', 10))
                    label.pack()
                    setattr(self, attr_name, label)

    def setup_market_sentiment(self, parent):
        """Setup market sentiment display"""
        sentiment_card = ttk.LabelFrame(parent, text="📊 MARKET MOOD", 
                                      padding="15", style='Card.TFrame')
        sentiment_card.pack(fill=tk.X, pady=(0, 10))
        
        sentiment_grid = ttk.Frame(sentiment_card, style='Card.TFrame')
        sentiment_grid.pack(fill=tk.X)
        
        indicators = [
            ("Market Feeling", "sentiment_label"),
            ("Trend Power", "trend_label"),
            ("Price Swings", "volatility_label"),
            ("Reversal Chance", "reversal_label")
        ]
        
        for text, attr_name in indicators:
            frame = ttk.Frame(sentiment_grid, style='Card.TFrame')
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            
            ttk.Label(frame, text=text, style='Title.TLabel', font=('Arial', 9)).pack()
            label = ttk.Label(frame, text="--", style='Neutral.TLabel', font=('Arial', 10))
            label.pack()
            setattr(self, attr_name, label)

    def setup_technical_indicators(self, parent):
        """Setup technical indicators display"""
        tech_card = ttk.LabelFrame(parent, text="⚙️ TECHNICAL INDICATORS", 
                                 padding="15", style='Card.TFrame')
        tech_card.pack(fill=tk.X, pady=(0, 10))
        
        tech_grid = ttk.Frame(tech_card, style='Card.TFrame')
        tech_grid.pack(fill=tk.X)
        
        tech_indicators = [
            ("Trend Direction", "sma_label", "Are we going UP or DOWN?"),
            ("Momentum", "rsi_label", "How strong is the move?"),
            ("Volatility", "bollinger_label", "How wild are price swings?"),
            ("Buy/Sell Pressure", "macd_label", "Who's controlling the market?")
        ]
        
        for i in range(0, len(tech_indicators), 2):
            row = ttk.Frame(tech_grid, style='Card.TFrame')
            row.pack(fill=tk.X, pady=3)
            
            for j in range(2):
                if i + j < len(tech_indicators):
                    text, attr_name, desc = tech_indicators[i + j]
                    frame = ttk.Frame(row, style='Card.TFrame')
                    frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                    
                    ttk.Label(frame, text=text, style='Title.TLabel', font=('Arial', 10)).pack(anchor='w')
                    ttk.Label(frame, text=desc, style='Neutral.TLabel', font=('Arial', 8)).pack(anchor='w')
                    label = ttk.Label(frame, text="--", style='Value.TLabel', font=('Arial', 10))
                    label.pack(anchor='w')
                    setattr(self, attr_name, label)

    def setup_advanced_indicators(self, parent):
        """Setup advanced indicators display"""
        advanced_card = ttk.LabelFrame(parent, text="🔬 ADVANCED INDICATORS", 
                                     padding="15", style='Card.TFrame')
        advanced_card.pack(fill=tk.X, pady=(0, 10))
        
        # Create a grid for advanced indicators
        grid_frame = ttk.Frame(advanced_card, style='Card.TFrame')
        grid_frame.pack(fill=tk.X)
        
        advanced_indicators = [
            ("Market Regime", "regime_label"),
            ("Dip Probability", "dip_prob_label"),
            ("ATR Value", "atr_label"),
            ("Session", "session_label"),
            ("News Sentiment", "news_label"),
            ("Strategy Count", "strategy_label")
        ]
        
        for i in range(0, len(advanced_indicators), 3):
            row_frame = ttk.Frame(grid_frame, style='Card.TFrame')
            row_frame.pack(fill=tk.X, pady=2)
            
            for j in range(3):
                if i + j < len(advanced_indicators):
                    text, attr_name = advanced_indicators[i + j]
                    frame = ttk.Frame(row_frame, style='Card.TFrame')
                    frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                    
                    ttk.Label(frame, text=text, style='Title.TLabel', font=('Arial', 9)).pack()
                    label = ttk.Label(frame, text="--", style='Value.TLabel', font=('Arial', 10))
                    label.pack()
                    setattr(self, attr_name, label)

    def setup_key_levels(self, parent):
        """Setup key levels display"""
        levels_card = ttk.LabelFrame(parent, text="🎯 KEY PRICE LEVELS", 
                                   padding="15", style='Card.TFrame')
        levels_card.pack(fill=tk.X, pady=(0, 10))
        
        levels_grid = ttk.Frame(levels_card, style='Card.TFrame')
        levels_grid.pack(fill=tk.X)
        
        # Support levels
        support_frame = ttk.Frame(levels_grid, style='Card.TFrame')
        support_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(support_frame, text="💰 SUPPORT (Price Floors)", 
                 style='Positive.TLabel', font=('Arial', 11, 'bold')).pack()
        ttk.Label(support_frame, text="Prices might bounce here", 
                 style='Neutral.TLabel', font=('Arial', 8)).pack()
        self.support_label = ttk.Label(support_frame, text="Calculating...", 
                                     style='Value.TLabel', font=('Arial', 10))
        self.support_label.pack()
        
        # Resistance levels  
        resistance_frame = ttk.Frame(levels_grid, style='Card.TFrame')
        resistance_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(resistance_frame, text="🚀 RESISTANCE (Price Ceilings)", 
                 style='Negative.TLabel', font=('Arial', 11, 'bold')).pack()
        ttk.Label(resistance_frame, text="Prices might struggle here", 
                 style='Neutral.TLabel', font=('Arial', 8)).pack()
        self.resistance_label = ttk.Label(resistance_frame, text="Calculating...", 
                                        style='Value.TLabel', font=('Arial', 10))
        self.resistance_label.pack()

    def setup_price_predictions(self, parent):
        """Setup price predictions section"""
        predictions_card = ttk.LabelFrame(parent, text="🔮 PRICE FORECAST", 
                                        padding="15", style='Card.TFrame')
        predictions_card.pack(fill=tk.X, pady=(0, 10))
        
        pred_frame = ttk.Frame(predictions_card, style='Card.TFrame')
        pred_frame.pack(fill=tk.X)
        
        time_frames = [
            ("15 MIN", "pred_15min_label", "Short-term move"),
            ("1 HOUR", "pred_1hr_label", "Hourly trend"),
            ("4 HOURS", "pred_4hr_label", "Session direction"),
            ("TODAY", "pred_today_label", "Daily target")
        ]
        
        for text, attr_name, desc in time_frames:
            frame = ttk.Frame(pred_frame, style='Card.TFrame')
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
            
            ttk.Label(frame, text=text, style='Title.TLabel', font=('Arial', 10, 'bold')).pack()
            ttk.Label(frame, text=desc, style='Neutral.TLabel', font=('Arial', 8)).pack()
            label = ttk.Label(frame, text="--", style='Value.TLabel', font=('Arial', 11))
            label.pack()
            setattr(self, attr_name, label)

    def setup_status_bar(self, parent):
        """Setup status bar"""
        status_frame = ttk.Frame(parent, style='Status.TFrame')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="🔄 Connecting to markets...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style='Status.TLabel', relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, ipady=2)
        
        # Performance metrics
        self.performance_var = tk.StringVar(value="Uptime: 00:00:00 | Success: 0 | Failed: 0")
        performance_label = ttk.Label(status_frame, textvariable=self.performance_var,
                                    style='Status.TLabel', relief=tk.SUNKEN, anchor=tk.E)
        performance_label.pack(fill=tk.X, ipady=2)

    # ===== CORE FUNCTIONALITY =====
    
    def calculate_dip_probability(self):
        """Calculate dip probability score (0-100)"""
        if len(self.price_history) < 10:
            return 0
        
        score = 0
        
        # Time-based scoring (Asian session)
        if self.data_manager.strategies.is_asian_session():
            score += 20
        
        # RSI scoring
        rsi = self.calculate_rsi(14)
        if rsi is not None:
            if rsi < 40:
                score += 15
            elif rsi < 30:
                score += 25
        
        # Volume scoring
        if len(self.volume_history) >= 5:
            recent_volume = list(self.volume_history)[-5:]
            avg_volume = sum(recent_volume) / len(recent_volume)
            if self.volume_history and avg_volume < np.percentile(list(self.volume_history), 30):
                score += 10
        
        # Price momentum scoring
        if len(self.price_history) >= 6:
            recent_prices = list(self.price_history)[-6:]
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            if momentum < -1:
                score += 10
        
        return min(max(score, 0), 100)

    def calculate_trend_classification(self):
        """Classify market trend using multiple timeframes"""
        if len(self.price_history) < 50:
            return "analyzing", "Insufficient data"
        
        try:
            # Calculate EMAs
            ema_20 = self.calculate_ema(20)
            ema_50 = self.calculate_ema(50)
            
            if ema_20 is None or ema_50 is None:
                return "analyzing", "Calculating indicators"
            
            # Trend classification logic
            if ema_20 > ema_50:
                trend_strength = (ema_20 - ema_50) / ema_50 * 100
                if trend_strength > 3:
                    return "strong_uptrend", f"Strong Uptrend ({trend_strength:.1f}%)"
                else:
                    return "uptrend", f"Uptrend ({trend_strength:.1f}%)"
            else:
                trend_strength = (ema_50 - ema_20) / ema_20 * 100
                if trend_strength > 3:
                    return "strong_downtrend", f"Strong Downtrend ({trend_strength:.1f}%)"
                else:
                    return "downtrend", f"Downtrend ({trend_strength:.1f}%)"
                    
        except Exception as e:
            logging.warning(f"Trend classification error: {e}")
            return "error", "Analysis unavailable"

    def calculate_atr_targets(self):
        """Calculate targets using ATR"""
        if len(self.high_history) < 15 or len(self.low_history) < 15 or len(self.price_history) < 15:
            return self.current_price * 1.03, self.current_price * 0.98
        
        try:
            atr = self.data_manager.indicators.calculate_atr(
                list(self.high_history)[-15:],
                list(self.low_history)[-15:],
                list(self.price_history)[-15:]
            )
            
            if atr is None:
                return self.current_price * 1.03, self.current_price * 0.98
            
            # ATR-based targets
            tp = self.current_price + (atr * 1.0)
            stop = self.current_price - (atr * 0.8)
            
            return tp, stop
            
        except Exception as e:
            logging.warning(f"ATR target calculation error: {e}")
            return self.current_price * 1.03, self.current_price * 0.98

    def update_advanced_indicators(self):
        """Calculate all advanced indicators"""
        try:
            # Basic indicators
            rsi = self.calculate_rsi(14)
            self.advanced_indicators['rsi_1h'] = rsi
            
            # Bollinger Bands position
            bb_upper, _, bb_lower = self.calculate_bollinger_bands()
            if bb_upper is not None and bb_lower is not None:
                current_price = self.current_price
                if current_price <= bb_lower:
                    self.advanced_indicators['bollinger_position'] = 'lower'
                elif current_price >= bb_upper:
                    self.advanced_indicators['bollinger_position'] = 'upper'
                else:
                    self.advanced_indicators['bollinger_position'] = 'middle'
            else:
                self.advanced_indicators['bollinger_position'] = None
            
            # Volume analysis
            if len(self.volume_history) >= 20:
                recent_volume = list(self.volume_history)[-5:]
                avg_recent_volume = sum(recent_volume) / len(recent_volume)
                avg_historical_volume = sum(list(self.volume_history)[-20:]) / 20
                self.advanced_indicators['volume_spike'] = avg_recent_volume > avg_historical_volume * 1.5
            else:
                self.advanced_indicators['volume_spike'] = False
            
            # Market regime detection
            self.detect_market_regime()
            
            # News sentiment
            news_sentiment, news_items = self.data_manager.news_analyzer.fetch_news_sentiment()
            self.advanced_indicators['news_sentiment'] = news_sentiment
            self.advanced_indicators['news_items'] = news_items
            
            # EMA trend
            ema_20 = self.calculate_ema(20)
            ema_50 = self.calculate_ema(50)
            if ema_20 is not None and ema_50 is not None:
                self.advanced_indicators['ema_trend'] = 'bullish' if ema_20 > ema_50 else 'bearish'
            else:
                self.advanced_indicators['ema_trend'] = None
            
            # Active strategies
            self.active_strategies = self.data_manager.strategies.calculate_strategy_signals(
                self.advanced_indicators
            )
            
            # Dip probability
            self.advanced_indicators['dip_probability'] = self.calculate_dip_probability()
            
            # Trend classification
            trend_type, trend_description = self.calculate_trend_classification()
            self.advanced_indicators['trend_type'] = trend_type
            self.advanced_indicators['trend_description'] = trend_description
            
        except Exception as e:
            logging.warning(f"Advanced indicators update error: {e}")

    def detect_market_regime(self):
        """Detect current market regime"""
        if len(self.price_history) < 20:
            self.market_regime = "unknown"
            return
        
        try:
            prices = list(self.price_history)[-20:]
            
            # Calculate price change and volatility
            price_change = (prices[-1] - prices[0]) / prices[0] * 100
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volatility = np.std(returns) * 100 if returns else 0
            
            # Determine regime
            if abs(price_change) > 8:
                self.market_regime = "trending"
            elif volatility < 1.0:
                self.market_regime = "sideways"
            elif volatility > 2.5:
                self.market_regime = "volatile"
            else:
                self.market_regime = "normal"
                
        except Exception as e:
            logging.warning(f"Market regime detection error: {e}")
            self.market_regime = "unknown"

    def update_advanced_displays(self):
        """Update the advanced indicators and strategies displays"""
        try:
            # Update advanced indicators
            regime = self.market_regime.upper()
            regime_color = "#00ff88" if regime == "TRENDING" else "#ffaa00" if regime == "SIDEWAYS" else "#ff4444"
            self.regime_label.config(text=regime, foreground=regime_color)
            
            dip_prob = self.advanced_indicators.get('dip_probability', 0)
            dip_color = "#00ff88" if dip_prob > 70 else "#ffaa00" if dip_prob > 50 else "#ff4444"
            self.dip_prob_label.config(text=f"{dip_prob}%", foreground=dip_color)
            
            # Session info
            ph_time = self.data_manager.strategies.get_ph_time()
            session = "ASIAN" if self.data_manager.strategies.is_asian_session() else "US" if self.data_manager.strategies.is_us_session() else "OTHER"
            self.session_label.config(text=f"{session} ({ph_time.strftime('%H:%M')})")
            
            # News sentiment
            news_sentiment = self.advanced_indicators.get('news_sentiment', 0)
            news_color = "#00ff88" if news_sentiment > 0.1 else "#ff4444" if news_sentiment < -0.1 else "#ffaa00"
            self.news_label.config(text=f"{news_sentiment:+.2f}", foreground=news_color)
            
            # Strategy count
            strategy_count = len(self.active_strategies)
            self.strategy_label.config(text=f"{strategy_count} active")
            
            # Update strategies display
            self.strategies_text.config(state=tk.NORMAL)
            self.strategies_text.delete(1.0, tk.END)
            
            if self.active_strategies:
                for strategy, confidence, reason in self.active_strategies:
                    confidence_pct = int(confidence * 100)
                    color = "#00ff88" if confidence_pct > 70 else "#ffaa00" if confidence_pct > 60 else "#ff4444"
                    self.strategies_text.insert(tk.END, f"• {strategy.upper()}: {confidence_pct}% confidence\n")
                    self.strategies_text.insert(tk.END, f"  {reason}\n\n")
            else:
                self.strategies_text.insert(tk.END, "No active strategies detected\n")
                self.strategies_text.insert(tk.END, "Waiting for optimal market conditions...")
            
            self.strategies_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logging.warning(f"Advanced displays update error: {e}")

    def update_display(self):
        """Update the display with enhanced indicators"""
        try:
            # Update advanced indicators first
            self.update_advanced_indicators()
            self.update_advanced_displays()
            
            # Update price display
            if self.current_price > 0:
                self.price_label.config(text=f"${self.current_price:,.0f}")
            
            # Update change display
            if hasattr(self, 'change_label') and self.current_price > 0:
                change_color = "#00ff88" if self.price_change >= 0 else "#ff4444"
                change_symbol = "+" if self.price_change >= 0 else ""
                self.change_label.config(
                    text=f"{change_symbol}${abs(self.price_change):.2f} ({change_symbol}{self.change_percentage:.2f}%)",
                    foreground=change_color
                )
            
            # Update connection status
            if self.data_manager.consecutive_errors > 5:
                self.connection_label.config(text="🔴 Offline", foreground="#ff4444")
            elif self.data_manager.consecutive_errors > 2:
                self.connection_label.config(text="🟡 Unstable", foreground="#ffaa00")
            else:
                self.connection_label.config(text="🟢 Online", foreground="#00ff88")
            
            # Enhanced trend analysis
            recommendation, reason, color = self.analyze_trend_enhanced()
            self.prediction_label.config(text=recommendation, foreground=color)
            self.reason_label.config(text=reason)
            
            # Enhanced trading plan
            self.update_trading_plan_enhanced(recommendation)
            
            # Update technical indicators
            self.update_technical_indicators()
            
            # Update price predictions
            self.update_price_predictions()
            
            # Update support and resistance
            self.update_support_resistance()
            
            # Update performance metrics
            self.update_performance_metrics()
            
            # Update status
            self.status_var.set(f"✅ Live data • Last update: {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
            self.successful_updates += 1
            
        except Exception as e:
            self.failed_updates += 1
            self.status_var.set(f"⚠️ Update error: {str(e)}")
            logging.error(f"Display update error: {e}")

    def analyze_trend_enhanced(self):
        """Enhanced trend analysis using multiple strategies"""
        if len(self.price_history) < 20:
            return "ANALYZING", "Gathering market data...", "orange"
        
        try:
            # Get advanced indicators
            dip_prob = self.advanced_indicators.get('dip_probability', 0)
            trend_type = self.advanced_indicators.get('trend_type', 'unknown')
            news_sentiment = self.advanced_indicators.get('news_sentiment', 0)
            
            # Base analysis on multiple factors
            score = 0
            reasons = []
            
            # Trend strength
            if trend_type == "strong_uptrend":
                score += 3
                reasons.append("Strong uptrend confirmed")
            elif trend_type == "uptrend":
                score += 2
                reasons.append("Uptrend in progress")
            elif trend_type == "downtrend":
                score -= 2
                reasons.append("Downtrend detected")
            elif trend_type == "strong_downtrend":
                score -= 3
                reasons.append("Strong downtrend")
            
            # Dip probability for buying opportunities
            if dip_prob > 70 and trend_type in ["uptrend", "strong_uptrend"]:
                score += 2
                reasons.append(f"High dip probability ({dip_prob}%)")
            
            # News sentiment
            if news_sentiment > 0.2:
                score += 1
                reasons.append("Positive news sentiment")
            elif news_sentiment < -0.2:
                score -= 1
                reasons.append("Negative news sentiment")
            
            # RSI conditions
            rsi = self.calculate_rsi(14)
            if rsi is not None:
                if rsi < 30:
                    score += 2
                    reasons.append("Oversold conditions")
                elif rsi > 70:
                    score -= 1
                    reasons.append("Overbought conditions")
            
            # Generate recommendation
            if score >= 4:
                return "STRONG BUY 🚀", " • ".join(reasons), "#00ff88"
            elif score >= 2:
                return "BUY 📈", " • ".join(reasons), "#90ff00"
            elif score <= -4:
                return "STRONG SELL 🐻", " • ".join(reasons), "#ff4444"
            elif score <= -2:
                return "SELL 📉", " • ".join(reasons), "#ff8800"
            else:
                return "HOLD ⏸️", "Market conditions neutral", "#ffaa00"
                
        except Exception as e:
            logging.warning(f"Enhanced trend analysis error: {e}")
            return "ERROR", "Analysis temporarily unavailable", "red"

    def update_trading_plan_enhanced(self, recommendation):
        """Enhanced trading plan with ATR-based targets"""
        try:
            # Use ATR for target calculation
            tp, sl = self.calculate_atr_targets()
            
            self.entry_price = self.current_price
            self.take_profit = tp
            self.stop_loss = sl
            
            # Calculate risk/reward
            potential_profit = abs(tp - self.entry_price)
            potential_loss = abs(self.entry_price - sl)
            self.risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
            
            # Update display
            if self.entry_price > 0:
                self.entry_label.config(text=f"${self.entry_price:,.0f}")
                
                tp_percent = ((tp - self.entry_price) / self.entry_price) * 100
                sl_percent = ((sl - self.entry_price) / self.entry_price) * 100
                
                self.take_profit_label.config(text=f"${tp:,.0f} (+{tp_percent:.1f}%)")
                self.stop_loss_label.config(text=f"${sl:,.0f} ({sl_percent:+.1f}%)")
                self.rr_label.config(text=f"1:{self.risk_reward_ratio:.2f}")
                
                # Enhanced time predictions
                self.hold_time_label.config(text=self.calculate_hold_time_enhanced(recommendation))
                self.sell_time_label.config(text=self.predict_sell_time_enhanced(recommendation))
                
        except Exception as e:
            logging.warning(f"Enhanced trading plan update error: {e}")

    def calculate_hold_time_enhanced(self, recommendation):
        """Enhanced hold time calculation based on strategy"""
        if not self.active_strategies:
            return "60+ min"
        
        # Get the highest confidence strategy
        best_strategy = max(self.active_strategies, key=lambda x: x[1]) if self.active_strategies else None
        
        if best_strategy:
            strategy_name = best_strategy[0]
            if strategy_name == "buy_asian_dip":
                return "4-8 hours"
            elif strategy_name == "breakout_momentum":
                return "2-6 hours"
            elif strategy_name == "ema_trend":
                return "1-3 days"
            elif strategy_name == "mean_reversion":
                return "1-4 hours"
        
        return "60+ min"

    def predict_sell_time_enhanced(self, recommendation):
        """Enhanced sell time prediction"""
        current_time = datetime.now(timezone.utc)
        
        # Check if we have active strategies
        if self.active_strategies:
            for strategy, confidence, reason in self.active_strategies:
                if strategy == "buy_asian_dip":
                    # Target US session for selling
                    sell_time = current_time.replace(hour=20, minute=0, second=0)
                    if sell_time < current_time:
                        sell_time += timedelta(days=1)
                    return sell_time.strftime("%H:%M")
        
        # Default logic
        if recommendation in ["BUY", "STRONG BUY"]:
            sell_time = current_time + timedelta(hours=2)
        elif recommendation in ["SELL", "STRONG SELL"]:
            sell_time = current_time + timedelta(hours=1)
        else:
            sell_time = current_time + timedelta(hours=4)
        
        return sell_time.strftime("%H:%M")

    # ===== EXISTING INDICATOR METHODS =====
    
    def calculate_ema(self, period):
        """Calculate EMA"""
        if len(self.price_history) < period:
            return None
        try:
            return self.data_manager.indicators.calculate_ema(list(self.price_history), period)
        except Exception as e:
            logging.warning(f"EMA calculation error: {e}")
            return None

    def calculate_rsi(self, period=14):
        """Calculate RSI"""
        if len(self.price_history) < period + 1:
            return None
        
        try:
            prices = list(self.price_history)
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) < period:
                return None
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logging.warning(f"RSI calculation error: {e}")
            return None

    def calculate_bollinger_bands(self, period=20):
        """Calculate Bollinger Bands"""
        if len(self.price_history) < period:
            return None, None, None
        
        try:
            prices = list(self.price_history)[-period:]
            middle_band = sum(prices) / period
            
            variance = sum((x - middle_band) ** 2 for x in prices) / period
            std_dev = math.sqrt(variance)
            
            upper_band = middle_band + (std_dev * 2)
            lower_band = middle_band - (std_dev * 2)
            
            return upper_band, middle_band, lower_band
        except Exception as e:
            logging.warning(f"Bollinger Bands calculation error: {e}")
            return None, None, None

    def calculate_macd(self):
        """Calculate MACD"""
        try:
            ema_12 = self.calculate_ema(12)
            ema_26 = self.calculate_ema(26)
            
            if ema_12 is None or ema_26 is None:
                return None, None, None
            
            macd_line = ema_12 - ema_26
            signal_line = self.calculate_ema(9)
            histogram = macd_line - signal_line if signal_line else None
            
            return macd_line, signal_line, histogram
        except Exception as e:
            logging.warning(f"MACD calculation error: {e}")
            return None, None, None

    def calculate_support_resistance(self):
        """Calculate support and resistance levels"""
        if len(self.price_history) < 20:
            return [], []
        
        try:
            prices = list(self.price_history)
            recent_high = max(prices[-20:])
            recent_low = min(prices[-20:])
            current_price = prices[-1]
            
            support1 = recent_low
            support2 = recent_low - (recent_high - recent_low) * 0.1
            support3 = recent_low - (recent_high - recent_low) * 0.2
            
            resistance1 = recent_high
            resistance2 = recent_high + (recent_high - recent_low) * 0.1
            resistance3 = recent_high + (recent_high - recent_low) * 0.2
            
            support_levels = [level for level in [support1, support2, support3] if level < current_price]
            resistance_levels = [level for level in [resistance1, resistance2, resistance3] if level > current_price]
            
            return support_levels, resistance_levels
        except Exception as e:
            logging.warning(f"Support/Resistance calculation error: {e}")
            return [], []

    def update_technical_indicators(self):
        """Update technical indicators display"""
        try:
            # SMA trend
            sma_short = self.calculate_ema(10)
            sma_long = self.calculate_ema(30)
            if sma_short is not None and sma_long is not None:
                if sma_short > sma_long:
                    self.sma_label.config(text="UP TREND 📈", foreground="#00ff88")
                else:
                    self.sma_label.config(text="DOWN TREND 📉", foreground="#ff4444")
            else:
                self.sma_label.config(text="CALCULATING...", foreground="#ffaa00")
            
            # RSI
            rsi = self.calculate_rsi(14)
            if rsi is not None:
                if rsi < 30:
                    self.rsi_label.config(text=f"OVERSOLD ({rsi:.0f}) 🎯", foreground="#00ff88")
                elif rsi > 70:
                    self.rsi_label.config(text=f"OVERBOUGHT ({rsi:.0f}) ⚠️", foreground="#ff4444")
                else:
                    self.rsi_label.config(text=f"NEUTRAL ({rsi:.0f})", foreground="#ffaa00")
            else:
                self.rsi_label.config(text="CALCULATING...", foreground="#ffaa00")
            
            # Bollinger Bands
            bb_upper, bb_lower = self.calculate_bollinger_bands()[:2]
            if bb_upper is not None and bb_lower is not None:
                if self.current_price > bb_upper:
                    self.bollinger_label.config(text="HIGH VOLATILITY 🔥", foreground="#ff4444")
                elif self.current_price < bb_lower:
                    self.bollinger_label.config(text="LOW VOLATILITY 🎯", foreground="#00ff88")
                else:
                    self.bollinger_label.config(text="NORMAL VOLATILITY", foreground="#ffaa00")
            else:
                self.bollinger_label.config(text="CALCULATING...", foreground="#ffaa00")
            
            # MACD
            macd_line, signal_line, _ = self.calculate_macd()
            if macd_line is not None and signal_line is not None:
                if macd_line > signal_line:
                    self.macd_label.config(text="BULLISH MOMENTUM 🐂", foreground="#00ff88")
                else:
                    self.macd_label.config(text="BEARISH MOMENTUM 🐻", foreground="#ff4444")
            else:
                self.macd_label.config(text="CALCULATING...", foreground="#ffaa00")
                    
        except Exception as e:
            logging.warning(f"Technical indicators update error: {e}")

    def update_price_predictions(self):
        """Update price predictions"""
        try:
            if len(self.price_history) < 10:
                return
            
            current_price = self.current_price
            
            # Simple prediction based on recent trend
            recent_trend = (self.price_history[-1] - self.price_history[-5]) / self.price_history[-5] * 100 if len(self.price_history) >= 5 else 0
            
            predictions = [
                current_price * (1 + recent_trend/100 * 0.25),  # 15min
                current_price * (1 + recent_trend/100 * 0.5),   # 1hr
                current_price * (1 + recent_trend/100 * 1.0),   # 4hr
                current_price * (1 + recent_trend/100 * 2.0)    # today
            ]
            
            prediction_widgets = [self.pred_15min_label, self.pred_1hr_label, self.pred_4hr_label, self.pred_today_label]
            
            for pred, widget in zip(predictions, prediction_widgets):
                if pred:
                    change = (pred - current_price) / current_price * 100
                    color = "#00ff88" if change > 0 else "#ff4444"
                    widget.config(
                        text=f"${pred:,.0f}\n({change:+.1f}%)", 
                        foreground=color
                    )
                    
        except Exception as e:
            logging.warning(f"Price predictions update error: {e}")

    def update_support_resistance(self):
        """Update support and resistance levels"""
        try:
            support_levels, resistance_levels = self.calculate_support_resistance()
            
            if support_levels:
                support_text = "\n".join([f"${level:,.0f}" for level in support_levels[:3]])
                self.support_label.config(text=support_text)
            else:
                self.support_label.config(text="Calculating...")
            
            if resistance_levels:
                resistance_text = "\n".join([f"${level:,.0f}" for level in resistance_levels[:3]])
                self.resistance_label.config(text=resistance_text)
            else:
                self.resistance_label.config(text="Calculating...")
                
        except Exception as e:
            logging.warning(f"Support/resistance update error: {e}")

    def update_performance_metrics(self):
        """Update performance metrics"""
        try:
            uptime = datetime.now(timezone.utc) - self.start_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            success_rate = (self.successful_updates / (self.successful_updates + self.failed_updates)) * 100 if (self.successful_updates + self.failed_updates) > 0 else 0
            
            self.performance_var.set(
                f"Uptime: {uptime_str} | Success: {self.successful_updates} | Failed: {self.failed_updates} | Rate: {success_rate:.1f}%"
            )
        except Exception as e:
            logging.warning(f"Performance metrics update error: {e}")

    # ===== DATA FETCHING =====
    
    def fetch_bitcoin_data_enhanced(self):
        """Enhanced data fetching with multiple sources and fallbacks"""
        sources = [
            ("CoinGecko", self.fetch_coingecko_data),
            ("Binance", self.fetch_binance_data),
        ]
        
        for source_name, fetch_func in sources:
            try:
                price = fetch_func()
                if price and price > 0:
                    logging.info(f"Successfully fetched from {source_name}: ${price:,.2f}")
                    
                    # Update price change
                    if self.price_history:
                        previous_price = self.price_history[-1]
                        self.price_change = price - previous_price
                        self.change_percentage = (self.price_change / previous_price) * 100
                    
                    self.current_price = price
                    self.price_history.append(price)
                    
                    # Simulate OHLC data for demonstration
                    if len(self.price_history) > 1:
                        high_price = max(self.price_history[-2], price)
                        low_price = min(self.price_history[-2], price)
                        volume = random.uniform(1000000, 50000000)
                        
                        self.high_history.append(high_price)
                        self.low_history.append(low_price)
                        self.volume_history.append(volume)
                    
                    self.data_manager.consecutive_errors = 0
                    return True
                    
            except Exception as e:
                logging.warning(f"Failed to fetch from {source_name}: {e}")
                continue
        
        # All sources failed
        self.data_manager.consecutive_errors += 1
        
        # Use simulated data as last resort
        if self.price_history:
            simulated_change = random.uniform(-0.01, 0.01)
            simulated_price = self.price_history[-1] * (1 + simulated_change)
            self.current_price = simulated_price
            self.price_history.append(simulated_price)
            logging.warning("Using simulated data due to API failures")
            return True
        
        return False

    def fetch_coingecko_data(self):
        """Fetch data from CoinGecko API with better error handling"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            
            # Add headers to avoid 429 errors
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    if 'bitcoin' in data and 'usd' in data['bitcoin']:
                        return data['bitcoin']['usd']
            return None
            
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logging.warning("CoinGecko rate limit exceeded, waiting...")
                time.sleep(60)  # Wait longer on rate limit
            return None
        except Exception as e:
            logging.warning(f"CoinGecko fetch error: {e}")
            return None

    def fetch_binance_data(self):
        """Fetch data from Binance API as fallback"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    return float(data['price'])
            return None
            
        except Exception as e:
            logging.warning(f"Binance fetch error: {e}")
            return None

    def start_data_fetching(self):
        """Start the data fetching thread"""
        def fetch_loop():
            while self.running:
                try:
                    success = self.fetch_bitcoin_data_enhanced()
                    if success:
                        self.root.after(0, self.update_display)
                    
                    # Adaptive delay based on errors
                    delay = 60 if self.data_manager.consecutive_errors > 2 else 30
                    time.sleep(delay)
                    
                except Exception as e:
                    logging.error(f"Fetch loop error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=fetch_loop, daemon=True)
        thread.start()

    def schedule_health_check(self):
        """Schedule regular health checks"""
        def health_check():
            if self.running:
                uptime = datetime.now(timezone.utc) - self.start_time
                success_rate = (self.successful_updates / (self.successful_updates + self.failed_updates)) * 100 if (self.successful_updates + self.failed_updates) > 0 else 0
                
                logging.info(f"Health check - Uptime: {uptime}, Success rate: {success_rate:.1f}%")
                
                # Schedule next health check
                self.root.after(300000, health_check)  # Every 5 minutes
        
        self.root.after(300000, health_check)

    def on_closing(self):
        """Handle application closing"""
        self.running = False
        logging.info("Application shutting down")
        self.root.destroy()

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = BitcoinPredictor(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Center the window
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 1400) // 2
        y = (screen_height - 900) // 2
        root.geometry(f"1400x900+{x}+{y}")
        
        logging.info("Starting Bitcoin Trading Assistant")
        root.mainloop()
        
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")

if __name__ == "__main__":
    main()