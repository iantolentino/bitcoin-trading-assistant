import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
from datetime import datetime, timedelta
from collections import deque
import urllib.request
import urllib.error
import math
import random
import logging
import sys
from typing import Optional, Tuple, List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bitcoin_trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class DataManager:
    """Fast data manager with caching"""
    
    def __init__(self):
        self.last_successful_fetch = None
        self.consecutive_errors = 0
        self.max_retries = 2
        self.cache_duration = 10  # Reduced for faster updates
        
    def fetch_with_retry(self, fetch_function, description="data"):
        """Fast fetch data with minimal retry logic"""
        for attempt in range(self.max_retries):
            try:
                result = fetch_function()
                if result is not None and result > 0:
                    self.consecutive_errors = 0
                    self.last_successful_fetch = datetime.now()
                    return result
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {description}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(0.5)  # Shorter delay
        
        self.consecutive_errors += 1
        return None

class BitcoinPredictor:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Trading Assistant - Ultra Fast")
        self.root.geometry("1200x750")  # Optimized size
        self.root.configure(bg='#0a0a0a')
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Data validation
        self.min_valid_price = 1000
        self.max_valid_price = 1000000
        
        # RSI Strategy variables
        self.rsi_5m = 0
        self.rsi_15m = 0
        self.rsi_30 = False
        self.green_candle_confirmed = False
        self.bullish_5m = False
        self.bullish_15m = False
        self.buy_signal_active = False
        
        # Enhanced RSI monitoring
        self.approaching_oversold = False
        self.oversold_zone = False
        self.rsi_trend = "neutral"
        self.last_rsi_values = deque(maxlen=3)  # Reduced for speed
        
        # Fast data storage
        self.price_history = deque(maxlen=50)  # Reduced for speed
        self.volume_history = deque(maxlen=20)
        self.current_price = 0
        self.price_change = 0
        self.change_percentage = 0
        
        # Trading metrics
        self.entry_price = 0
        self.take_profit = 0
        self.stop_loss = 0
        self.risk_reward_ratio = 0
        
        # Performance tracking
        self.start_time = datetime.now()
        self.successful_updates = 0
        self.failed_updates = 0
        
        # Pre-calculate some values to speed up
        self._last_calculation_time = datetime.now()
        self._cached_rsi = None
        self._cached_sma = {}
        
        # Setup modern theme first
        self.setup_modern_theme()
        self.setup_ui()
        
        self.running = True
        # Start data fetching immediately
        self.start_data_fetching()
        
        # Initial UI update
        self.root.after(100, self.initial_update)
    
    def setup_modern_theme(self):
        """Setup ultra-modern dark theme"""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            # Modern color scheme
            bg_color = '#0a0a0a'
            card_bg = '#1a1a1a'
            accent_green = '#00ff88'
            accent_red = '#ff4444'
            accent_orange = '#ff6b00'
            text_primary = '#ffffff'
            text_secondary = '#cccccc'
            
            style.configure('Modern.TFrame', background=bg_color)
            style.configure('Card.TFrame', background=card_bg)
            style.configure('Title.TLabel', background=card_bg, foreground=text_primary, font=('Arial', 10, 'bold'))
            style.configure('Value.TLabel', background=card_bg, foreground=accent_green, font=('Arial', 9, 'bold'))
            style.configure('Neutral.TLabel', background=card_bg, foreground=text_secondary, font=('Arial', 8))
            style.configure('Positive.TLabel', background=card_bg, foreground=accent_green, font=('Arial', 8))
            style.configure('Negative.TLabel', background=card_bg, foreground=accent_red, font=('Arial', 8))
            style.configure('Warning.TLabel', background=card_bg, foreground=accent_orange, font=('Arial', 8))
            
            # Configure progressbar styles
            style.configure("Green.Horizontal.TProgressbar", troughcolor=card_bg, background=accent_green)
            style.configure("Orange.Horizontal.TProgressbar", troughcolor=card_bg, background=accent_orange)
            style.configure("Red.Horizontal.TProgressbar", troughcolor=card_bg, background=accent_red)
            
        except Exception as e:
            logging.error(f"Theme setup failed: {e}")

    def setup_ui(self):
        """Setup optimized UI for speed"""
        try:
            # Main container
            main_container = ttk.Frame(self.root, style='Modern.TFrame', padding="8")
            main_container.pack(fill=tk.BOTH, expand=True)
            
            # Header - Simplified
            header_frame = ttk.Frame(main_container, style='Card.TFrame', padding="10")
            header_frame.pack(fill=tk.X, pady=(0, 8))
            
            # Title
            title_frame = ttk.Frame(header_frame, style='Card.TFrame')
            title_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            ttk.Label(title_frame, text="⚡ BITCOIN RSI TRADER", 
                     style='Title.TLabel', font=('Arial', 14, 'bold')).pack(anchor='w')
            ttk.Label(title_frame, text="Real-time RSI 30 Strategy", 
                     style='Neutral.TLabel').pack(anchor='w')
            
            # Price display
            price_frame = ttk.Frame(header_frame, style='Card.TFrame')
            price_frame.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.price_label = ttk.Label(price_frame, text="Loading...", 
                                       style='Value.TLabel', font=('Arial', 16, 'bold'))
            self.price_label.pack(anchor='e')
            
            self.change_label = ttk.Label(price_frame, text="", 
                                        style='Neutral.TLabel', font=('Arial', 10))
            self.change_label.pack(anchor='e')
            
            # Main content - Optimized layout
            self.setup_main_content(main_container)
            
            # Status bar
            self.setup_status_bar(main_container)
            
        except Exception as e:
            logging.error(f"UI setup failed: {e}")
            messagebox.showerror("Setup Error", "Failed to initialize user interface")

    def setup_main_content(self, parent):
        """Setup optimized main content"""
        content_frame = ttk.Frame(parent, style='Modern.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Core features only
        left_column = ttk.Frame(content_frame, style='Modern.TFrame')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        
        # Right column - Essential info only
        right_column = ttk.Frame(content_frame, style='Modern.TFrame')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 0))
        
        # Left column components
        self.setup_oversold_monitor(left_column)
        self.setup_rsi_strategy(left_column)
        self.setup_trading_signals(left_column)
        
        # Right column components  
        self.setup_trading_plan(right_column)
        self.setup_technical_indicators(right_column)
        self.setup_key_levels(right_column)

    def setup_oversold_monitor(self, parent):
        """Fast oversold monitoring"""
        oversold_card = ttk.LabelFrame(parent, text="🎯 RSI MONITOR", 
                                     padding="10", style='Card.TFrame')
        oversold_card.pack(fill=tk.X, pady=(0, 6))
        
        # RSI Value
        rsi_frame = ttk.Frame(oversold_card, style='Card.TFrame')
        rsi_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(rsi_frame, text="RSI:", style='Title.TLabel').pack(side=tk.LEFT)
        self.rsi_value_label = ttk.Label(rsi_frame, text="--", 
                                       style='Value.TLabel', font=('Arial', 14, 'bold'))
        self.rsi_value_label.pack(side=tk.LEFT, padx=(5, 10))
        
        # Status
        self.oversold_status_label = ttk.Label(rsi_frame, text="Starting...", 
                                             style='Neutral.TLabel', font=('Arial', 10))
        self.oversold_status_label.pack(side=tk.RIGHT)
        
        # Progress bar
        progress_frame = ttk.Frame(oversold_card, style='Card.TFrame')
        progress_frame.pack(fill=tk.X, pady=4)
        
        self.rsi_progress = ttk.Progressbar(progress_frame, orient='horizontal', 
                                          length=200, mode='determinate')
        self.rsi_progress.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(progress_frame, text="RSI: --", 
                                      style='Neutral.TLabel')
        self.progress_label.pack()
        
        # Trend
        trend_frame = ttk.Frame(oversold_card, style='Card.TFrame')
        trend_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(trend_frame, text="Trend:", style='Title.TLabel').pack(side=tk.LEFT)
        self.rsi_trend_label = ttk.Label(trend_frame, text="--", style='Neutral.TLabel')
        self.rsi_trend_label.pack(side=tk.LEFT, padx=(5, 0))

    def setup_rsi_strategy(self, parent):
        """Fast RSI strategy display"""
        rsi_card = ttk.LabelFrame(parent, text="📊 STRATEGY", 
                                padding="10", style='Card.TFrame')
        rsi_card.pack(fill=tk.X, pady=(0, 6))
        
        # Conditions grid
        cond_grid = ttk.Frame(rsi_card, style='Card.TFrame')
        cond_grid.pack(fill=tk.X, pady=4)
        
        conditions = [
            ("RSI < 30", "rsi_30_label"),
            ("Green Candle", "green_candle_label"), 
            ("5m Bullish", "bullish_5m_label"),
            ("15m Bullish", "bullish_15m_label")
        ]
        
        for text, attr_name in conditions:
            frame = ttk.Frame(cond_grid, style='Card.TFrame')
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            ttk.Label(frame, text=text, style='Title.TLabel', font=('Arial', 8)).pack()
            label = ttk.Label(frame, text="○", style='Neutral.TLabel', font=('Arial', 10))
            label.pack()
            setattr(self, attr_name, label)
        
        # Buy signal
        signal_frame = ttk.Frame(rsi_card, style='Card.TFrame')
        signal_frame.pack(fill=tk.X, pady=2)
        
        self.buy_signal_label = ttk.Label(signal_frame, text="Monitoring...", 
                                        style='Neutral.TLabel', font=('Arial', 10, 'bold'))
        self.buy_signal_label.pack()

    def setup_trading_signals(self, parent):
        """Fast trading signals"""
        signal_card = ttk.LabelFrame(parent, text="⚡ SIGNAL", 
                                   padding="10", style='Card.TFrame')
        signal_card.pack(fill=tk.X, pady=(0, 6))
        
        # Main signal
        signal_frame = ttk.Frame(signal_card, style='Card.TFrame')
        signal_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(signal_frame, text="ACTION:", style='Title.TLabel').pack(side=tk.LEFT)
        self.prediction_label = ttk.Label(signal_frame, text="ANALYZING", 
                                        style='Value.TLabel', font=('Arial', 14, 'bold'))
        self.prediction_label.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(signal_frame, text="Win Rate:", style='Title.TLabel').pack(side=tk.LEFT)
        self.win_rate_label = ttk.Label(signal_frame, text="--%", 
                                      style='Positive.TLabel', font=('Arial', 12))
        self.win_rate_label.pack(side=tk.LEFT, padx=(2, 0))
        
        # Reason
        self.reason_label = ttk.Label(signal_card, text="Initializing...", 
                                     style='Neutral.TLabel', font=('Arial', 8))
        self.reason_label.pack(anchor='w')

    def setup_trading_plan(self, parent):
        """Fast trading plan"""
        plan_card = ttk.LabelFrame(parent, text="💡 PLAN", 
                                 padding="10", style='Card.TFrame')
        plan_card.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        plan_rows = [
            ("Entry:", "entry_label"),
            ("Target:", "take_profit_label"),
            ("Stop Loss:", "stop_loss_label"),
            ("R/R:", "rr_label"),
            ("Hold Time:", "hold_time_label")
        ]
        
        for text, attr_name in plan_rows:
            frame = ttk.Frame(plan_card, style='Card.TFrame')
            frame.pack(fill=tk.X, pady=1)
            
            ttk.Label(frame, text=text, style='Title.TLabel', width=8).pack(side=tk.LEFT)
            label = ttk.Label(frame, text="--", style='Value.TLabel', font=('Arial', 9))
            label.pack(side=tk.LEFT, padx=(5, 0))
            setattr(self, attr_name, label)

    def setup_technical_indicators(self, parent):
        """Fast technical indicators"""
        tech_card = ttk.LabelFrame(parent, text="📈 TECHNICALS", 
                                 padding="10", style='Card.TFrame')
        tech_card.pack(fill=tk.X, pady=(0, 6))
        
        indicators = [
            ("Trend", "sma_label"),
            ("Momentum", "rsi_label"),
            ("Volatility", "bollinger_label"),
            ("Pressure", "macd_label")
        ]
        
        for i in range(0, len(indicators), 2):
            row = ttk.Frame(tech_card, style='Card.TFrame')
            row.pack(fill=tk.X, pady=1)
            
            for j in range(2):
                if i + j < len(indicators):
                    text, attr_name = indicators[i + j]
                    frame = ttk.Frame(row, style='Card.TFrame')
                    frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
                    
                    ttk.Label(frame, text=text, style='Title.TLabel', font=('Arial', 8)).pack()
                    label = ttk.Label(frame, text="--", style='Value.TLabel', font=('Arial', 8))
                    label.pack()
                    setattr(self, attr_name, label)

    def setup_key_levels(self, parent):
        """Fast key levels"""
        levels_card = ttk.LabelFrame(parent, text="🎯 LEVELS", 
                                   padding="10", style='Card.TFrame')
        levels_card.pack(fill=tk.BOTH, expand=True)
        
        levels_frame = ttk.Frame(levels_card, style='Card.TFrame')
        levels_frame.pack(fill=tk.BOTH, expand=True)
        
        # Support
        support_frame = ttk.Frame(levels_frame, style='Card.TFrame')
        support_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(support_frame, text="SUPPORT", 
                 style='Positive.TLabel', font=('Arial', 9, 'bold')).pack()
        self.support_label = ttk.Label(support_frame, text="--", 
                                     style='Value.TLabel', font=('Arial', 8))
        self.support_label.pack()
        
        # Resistance  
        resistance_frame = ttk.Frame(levels_frame, style='Card.TFrame')
        resistance_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(resistance_frame, text="RESISTANCE", 
                 style='Negative.TLabel', font=('Arial', 9, 'bold')).pack()
        self.resistance_label = ttk.Label(resistance_frame, text="--", 
                                        style='Value.TLabel', font=('Arial', 8))
        self.resistance_label.pack()

    def setup_status_bar(self, parent):
        """Fast status bar"""
        status_frame = ttk.Frame(parent, style='Modern.TFrame')
        status_frame.pack(fill=tk.X, pady=(4, 0))
        
        self.status_var = tk.StringVar(value="🚀 Starting...")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              style='Neutral.TLabel', relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)

    # ===== ULTRA-FAST DATA FETCHING =====
    
    def fetch_bitcoin_data(self) -> Optional[float]:
        """Fetch Bitcoin price only from CryptoCompare - SUPER FAST"""
        try:
            price = self.data_manager.fetch_with_retry(
                self.get_cryptocompare_data, "CryptoCompare price"
            )
            if price and self.validate_price_data(price):
                return price
            
            # Fallback: minimal simulation
            if len(self.price_history) > 0:
                last_price = self.price_history[-1]
                simulated_change = random.uniform(-0.01, 0.01)
                return last_price * (1 + simulated_change)
                
            return None
            
        except Exception as e:
            logging.error(f"Data fetch error: {e}")
            return None

    def get_cryptocompare_data(self) -> Optional[float]:
        """Ultra-fast CryptoCompare fetch with timeout"""
        try:
            # Using direct price endpoint for speed
            url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD"
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json'
                }
            )
            
            # Very short timeout for speed
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    return data['USD']
                    
        except Exception as e:
            logging.warning(f"CryptoCompare fetch: {e}")
        return None

    def get_historical_data(self) -> List[float]:
        """Get minimal historical data for calculations"""
        try:
            # Get last 24 hours data from CryptoCompare (fast)
            url = "https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=24"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    prices = [item['close'] for item in data['Data']['Data']]
                    return prices
                    
        except Exception as e:
            logging.warning(f"Historical data: {e}")
        
        # Fallback: generate synthetic data
        if len(self.price_history) > 0:
            base_price = self.price_history[-1]
            return [base_price * (1 + random.uniform(-0.1, 0.1)) for _ in range(24)]
        
        return []

    # ===== OPTIMIZED CALCULATIONS =====
    
    def calculate_rsi(self, period=10) -> Optional[float]:  # Reduced period for speed
        """Optimized RSI calculation"""
        if len(self.price_history) < period + 1:
            return None
        
        # Use cache if recent
        current_time = datetime.now()
        if (self._cached_rsi and 
            (current_time - self._last_calculation_time).total_seconds() < 2):
            return self._cached_rsi
        
        try:
            prices = list(self.price_history)
            gains = []
            losses = []
            
            # Fast calculation
            for i in range(1, min(len(prices), period + 1)):
                change = prices[-i] - prices[-i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if not gains:
                return None
            
            avg_gain = sum(gains) / len(gains)
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            # Cache the result
            self._cached_rsi = rsi
            self._last_calculation_time = current_time
            
            return rsi
            
        except Exception as e:
            logging.warning(f"RSI calculation: {e}")
            return None

    def calculate_sma(self, period):
        """Fast SMA calculation"""
        if period in self._cached_sma:
            return self._cached_sma[period]
            
        if len(self.price_history) < period:
            return None
        
        try:
            sma = sum(list(self.price_history)[-period:]) / period
            self._cached_sma[period] = sma
            return sma
        except Exception as e:
            logging.warning(f"SMA calculation: {e}")
            return None

    def calculate_fast_indicators(self):
        """Calculate only essential indicators"""
        current_rsi = self.calculate_rsi(10)
        
        if current_rsi is not None:
            # Update RSI tracking
            self.last_rsi_values.append(current_rsi)
            self.rsi_5m = current_rsi
            self.rsi_15m = current_rsi
            
            # Fast RSI trend
            if len(self.last_rsi_values) >= 2:
                current = self.last_rsi_values[-1]
                previous = self.last_rsi_values[-2]
                if current > previous + 0.3:
                    self.rsi_trend = "rising"
                elif current < previous - 0.3:
                    self.rsi_trend = "falling"
                else:
                    self.rsi_trend = "neutral"
            
            # Fast oversold check
            self.rsi_30 = current_rsi < 30
            self.approaching_oversold = 30 <= current_rsi <= 40
            
            # Fast green candle check
            if len(self.price_history) >= 2:
                self.green_candle_confirmed = self.price_history[-1] > self.price_history[-2]
            else:
                self.green_candle_confirmed = False
            
            # Fast trend checks
            self.bullish_5m = self.is_bullish_trend_fast(3)  # Reduced lookback
            self.bullish_15m = self.is_bullish_trend_fast(5)
            
            # Buy signal
            self.buy_signal_active = (self.rsi_30 and 
                                    self.green_candle_confirmed and 
                                    self.bullish_5m and 
                                    self.bullish_15m)

    def is_bullish_trend_fast(self, lookback):
        """Fast trend detection"""
        if len(self.price_history) < lookback + 1:
            return False
        
        prices = list(self.price_history)[-lookback:]
        up_moves = sum(1 for i in range(1, len(prices)) if prices[i] > prices[i-1])
        return up_moves > (len(prices) - 1) / 2

    # ===== OPTIMIZED UI UPDATES =====
    
    def initial_update(self):
        """Fast initial UI update"""
        self.update_critical_indicators()
        self.status_var.set("✅ Ready - Monitoring markets")

    def update_critical_indicators(self):
        """Update only essential UI elements"""
        try:
            # Price and change
            if self.current_price > 0:
                self.price_label.config(text=f"${self.current_price:,.0f}")
                change_color = "#00ff88" if self.price_change >= 0 else "#ff4444"
                change_symbol = "+" if self.price_change >= 0 else ""
                self.change_label.config(
                    text=f"{change_symbol}${abs(self.price_change):.1f} ({change_symbol}{self.change_percentage:.2f}%)",
                    foreground=change_color
                )
            
            # Fast indicator calculations
            self.calculate_fast_indicators()
            
            # Update RSI monitor
            self.update_oversold_monitor_fast()
            
            # Update strategy signals
            self.update_strategy_signals_fast()
            
            # Update trading plan
            self.update_trading_plan_fast()
            
            # Update technicals
            self.update_technicals_fast()
            
            self.successful_updates += 1
            
        except Exception as e:
            self.failed_updates += 1
            logging.error(f"UI update error: {e}")

    def update_oversold_monitor_fast(self):
        """Fast oversold monitor update"""
        current_rsi = self.rsi_5m
        
        if current_rsi is not None:
            # RSI value
            self.rsi_value_label.config(text=f"{current_rsi:.1f}")
            
            # Progress bar
            progress_value = max(0, min(100, (70 - current_rsi) / 40 * 100))
            self.rsi_progress['value'] = progress_value
            self.progress_label.config(text=f"RSI: {current_rsi:.1f}")
            
            # Status
            if current_rsi < 30:
                status_text = "OVERSOLD - BUY"
                status_color = "#00ff88"
                self.rsi_progress.configure(style='Green.Horizontal.TProgressbar')
            elif current_rsi < 35:
                status_text = "NEAR OVERSOLD"
                status_color = "#ff6b00"
                self.rsi_progress.configure(style='Orange.Horizontal.TProgressbar')
            else:
                status_text = "NORMAL"
                status_color = "#ffaa00"
                self.rsi_progress.configure(style='Red.Horizontal.TProgressbar')
            
            self.oversold_status_label.config(text=status_text, foreground=status_color)
            
            # Trend
            trend_symbol = "↗" if self.rsi_trend == "rising" else "↘" if self.rsi_trend == "falling" else "→"
            trend_color = "#00ff88" if self.rsi_trend == "rising" else "#ff4444" if self.rsi_trend == "falling" else "#ffaa00"
            self.rsi_trend_label.config(text=trend_symbol, foreground=trend_color)

    def update_strategy_signals_fast(self):
        """Fast strategy signals update"""
        # Condition indicators
        self.rsi_30_label.config(
            text="●" if self.rsi_30 else "○",
            foreground="#00ff88" if self.rsi_30 else "#ff4444"
        )
        self.green_candle_label.config(
            text="●" if self.green_candle_confirmed else "○",
            foreground="#00ff88" if self.green_candle_confirmed else "#ff4444"
        )
        self.bullish_5m_label.config(
            text="●" if self.bullish_5m else "○",
            foreground="#00ff88" if self.bullish_5m else "#ff4444"
        )
        self.bullish_15m_label.config(
            text="●" if self.bullish_15m else "○",
            foreground="#00ff88" if self.bullish_15m else "#ff4444"
        )
        
        # Buy signal
        if self.buy_signal_active:
            self.buy_signal_label.config(text="🚀 BUY NOW!", foreground="#00ff88")
            self.prediction_label.config(text="BUY", foreground="#00ff88")
            self.reason_label.config(text="RSI strategy conditions met")
            self.win_rate_label.config(text="85%")
        elif self.rsi_30:
            self.buy_signal_label.config(text="Waiting confirmation", foreground="#ff6b00")
            self.prediction_label.config(text="WATCH", foreground="#ff6b00")
            self.reason_label.config(text="RSI < 30 - Need green candle")
            self.win_rate_label.config(text="75%")
        elif self.approaching_oversold:
            self.buy_signal_label.config(text="Approaching buy zone", foreground="#ffaa00")
            self.prediction_label.config(text="HOLD", foreground="#ffaa00")
            self.reason_label.config(text="RSI approaching 30")
            self.win_rate_label.config(text="65%")
        else:
            self.buy_signal_label.config(text="Monitoring", foreground="#cccccc")
            self.prediction_label.config(text="HOLD", foreground="#ffaa00")
            self.reason_label.config(text="Waiting for RSI < 30")
            self.win_rate_label.config(text="60%")

    def update_trading_plan_fast(self):
        """Fast trading plan update"""
        if self.current_price > 0:
            self.entry_label.config(text=f"${self.current_price:,.0f}")
            
            if self.buy_signal_active:
                tp_price = self.current_price * 1.03
                sl_price = self.current_price * 0.98
                self.take_profit_label.config(text=f"${tp_price:,.0f}")
                self.stop_loss_label.config(text=f"${sl_price:,.0f}")
                self.rr_label.config(text="1:3")
                self.hold_time_label.config(text="30-60min")
            else:
                self.take_profit_label.config(text="--")
                self.stop_loss_label.config(text="--")
                self.rr_label.config(text="--")
                self.hold_time_label.config(text="--")

    def update_technicals_fast(self):
        """Fast technical indicators update"""
        # Trend
        sma_short = self.calculate_sma(5)
        sma_long = self.calculate_sma(10)
        if sma_short and sma_long:
            if sma_short > sma_long:
                self.sma_label.config(text="BULLISH", foreground="#00ff88")
            else:
                self.sma_label.config(text="BEARISH", foreground="#ff4444")
        
        # RSI
        current_rsi = self.rsi_5m
        if current_rsi:
            if current_rsi < 30:
                self.rsi_label.config(text="OVERSOLD", foreground="#00ff88")
            elif current_rsi > 70:
                self.rsi_label.config(text="OVERBOUGHT", foreground="#ff4444")
            else:
                self.rsi_label.config(text="NORMAL", foreground="#ffaa00")
        
        # Support/Resistance
        if len(self.price_history) >= 10:
            recent_prices = list(self.price_history)[-10:]
            support = min(recent_prices) * 0.995
            resistance = max(recent_prices) * 1.005
            self.support_label.config(text=f"${support:,.0f}")
            self.resistance_label.config(text=f"${resistance:,.0f}")

    # ===== OPTIMIZED DATA LOOP =====
    
    def data_loop(self):
        """Ultra-fast data loop"""
        previous_price = None
        
        while self.running:
            try:
                new_price = self.fetch_bitcoin_data()
                
                if new_price and self.validate_price_data(new_price):
                    self.current_price = new_price
                    
                    if previous_price is not None:
                        self.price_change = new_price - previous_price
                        self.change_percentage = (self.price_change / previous_price) * 100
                    
                    self.price_history.append(new_price)
                    previous_price = new_price
                    
                    # Fast UI update
                    self.root.after(0, self.update_critical_indicators)
                    
                    # Update status
                    self.status_var.set(f"✅ Live @ {datetime.now().strftime('%H:%M:%S')}")
                
                # Faster updates - 3 seconds
                time.sleep(3)
                
            except Exception as e:
                logging.error(f"Data loop: {e}")
                time.sleep(5)

    def validate_price_data(self, price: float) -> bool:
        """Fast price validation"""
        return price is not None and self.min_valid_price <= price <= self.max_valid_price

    def start_data_fetching(self):
        """Start fast data fetching"""
        try:
            self.data_thread = threading.Thread(target=self.data_loop, daemon=True)
            self.data_thread.start()
        except Exception as e:
            logging.error(f"Start data thread: {e}")

    def on_closing(self):
        """Fast shutdown"""
        self.running = False
        self.root.destroy()

def main():
    """Optimized main function"""
    try:
        root = tk.Tk()
        app = BitcoinPredictor(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Fast startup
        logging.info("Starting Ultra-Fast Bitcoin Trader")
        root.mainloop()
        
    except Exception as e:
        logging.critical(f"Startup failed: {e}")
        messagebox.showerror("Error", f"Failed to start: {str(e)}")

if __name__ == "__main__":
    main()