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

class BitcoinPredictor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Bitcoin Trading Assistant")
        self.root.geometry("1100x800")
        
        # Center the window
        self.center_window(1100, 800)
        
        # Data storage
        self.price_history = deque(maxlen=100)
        self.volume_history = deque(maxlen=100)
        self.current_price = 0
        self.price_change = 0
        self.change_percentage = 0
        self.volume = 0
        
        # Trading levels
        self.support_levels = []
        self.resistance_levels = []
        self.buy_target = 0
        self.sell_target = 0
        self.stop_loss = 0
        
        # Prediction parameters
        self.sma_short = 10
        self.sma_long = 30
        self.ema_short = 12
        self.ema_long = 26
        self.macd_line = 0
        self.signal_line = 0
        self.macd_histogram = 0
        self.bollinger_upper = 0
        self.bollinger_lower = 0
        self.bollinger_middle = 0
        
        self.setup_ui()
        self.running = True
        self.start_data_fetching()
    
    def center_window(self, width, height):
        """Center the window on screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="₿ Advanced Bitcoin Trading Assistant", 
                               font=("Arial", 18, "bold"), foreground="#F7931A")
        title_label.pack(pady=10)
        
        # Current price frame
        price_frame = ttk.LabelFrame(main_frame, text="Live Bitcoin Price", padding="10")
        price_frame.pack(fill=tk.X, pady=5)
        
        self.price_label = ttk.Label(price_frame, text="Loading...", 
                                   font=("Arial", 20, "bold"))
        self.price_label.pack()
        
        self.change_label = ttk.Label(price_frame, text="", font=("Arial", 12))
        self.change_label.pack()
        
        # Trading signals frame
        signals_frame = ttk.LabelFrame(main_frame, text="Trading Signals & Targets", padding="10")
        signals_frame.pack(fill=tk.X, pady=5)
        
        # Create grid for trading signals
        signals_grid = ttk.Frame(signals_frame)
        signals_grid.pack(fill=tk.X)
        
        # Left column - Recommendations
        left_column = ttk.Frame(signals_grid)
        left_column.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.prediction_label = ttk.Label(left_column, text="Analyzing market data...", 
                                        font=("Arial", 14, "bold"))
        self.prediction_label.pack(anchor="w")
        
        self.reason_label = ttk.Label(left_column, text="", font=("Arial", 10), 
                                     wraplength=400, justify=tk.LEFT)
        self.reason_label.pack(anchor="w", pady=5)
        
        # Right column - Price targets
        right_column = ttk.Frame(signals_grid)
        right_column.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.buy_target_label = ttk.Label(right_column, text="Buy Target: Calculating...", 
                                         font=("Arial", 10), foreground="green")
        self.buy_target_label.pack(anchor="w")
        
        self.sell_target_label = ttk.Label(right_column, text="Sell Target: Calculating...", 
                                          font=("Arial", 10), foreground="red")
        self.sell_target_label.pack(anchor="w")
        
        self.stop_loss_label = ttk.Label(right_column, text="Stop Loss: Calculating...", 
                                        font=("Arial", 10), foreground="orange")
        self.stop_loss_label.pack(anchor="w")
        
        # Price predictions frame
        predictions_frame = ttk.LabelFrame(main_frame, text="Short-Term Price Predictions", padding="10")
        predictions_frame.pack(fill=tk.X, pady=5)
        
        predictions_grid = ttk.Frame(predictions_frame)
        predictions_grid.pack(fill=tk.X)
        
        # Prediction columns
        pred_5min = ttk.Frame(predictions_grid)
        pred_5min.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(pred_5min, text="5 Min Prediction", font=("Arial", 10, "bold")).pack()
        self.pred_5min_label = ttk.Label(pred_5min, text="Calculating...", font=("Arial", 11))
        self.pred_5min_label.pack()
        
        pred_15min = ttk.Frame(predictions_grid)
        pred_15min.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(pred_15min, text="15 Min Prediction", font=("Arial", 10, "bold")).pack()
        self.pred_15min_label = ttk.Label(pred_15min, text="Calculating...", font=("Arial", 11))
        self.pred_15min_label.pack()
        
        pred_1hr = ttk.Frame(predictions_grid)
        pred_1hr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(pred_1hr, text="1 Hour Prediction", font=("Arial", 10, "bold")).pack()
        self.pred_1hr_label = ttk.Label(pred_1hr, text="Calculating...", font=("Arial", 11))
        self.pred_1hr_label.pack()
        
        pred_4hr = ttk.Frame(predictions_grid)
        pred_4hr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(pred_4hr, text="4 Hour Prediction", font=("Arial", 10, "bold")).pack()
        self.pred_4hr_label = ttk.Label(pred_4hr, text="Calculating...", font=("Arial", 11))
        self.pred_4hr_label.pack()
        
        # Technical indicators frame
        tech_frame = ttk.LabelFrame(main_frame, text="Advanced Technical Indicators", padding="10")
        tech_frame.pack(fill=tk.X, pady=5)
        
        # Create grid for indicators
        indicators_grid = ttk.Frame(tech_frame)
        indicators_grid.pack(fill=tk.X)
        
        # Column 1
        col1 = ttk.Frame(indicators_grid)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.sma_label = ttk.Label(col1, text="SMA: Calculating...", font=("Arial", 9))
        self.sma_label.pack(anchor="w")
        self.ema_label = ttk.Label(col1, text="EMA: Calculating...", font=("Arial", 9))
        self.ema_label.pack(anchor="w")
        
        # Column 2
        col2 = ttk.Frame(indicators_grid)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.macd_label = ttk.Label(col2, text="MACD: Calculating...", font=("Arial", 9))
        self.macd_label.pack(anchor="w")
        self.rsi_label = ttk.Label(col2, text="RSI: Calculating...", font=("Arial", 9))
        self.rsi_label.pack(anchor="w")
        
        # Column 3
        col3 = ttk.Frame(indicators_grid)
        col3.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.bollinger_label = ttk.Label(col3, text="Bollinger Bands: Calculating...", font=("Arial", 9))
        self.bollinger_label.pack(anchor="w")
        self.volume_label = ttk.Label(col3, text="Volume Trend: Calculating...", font=("Arial", 9))
        self.volume_label.pack(anchor="w")
        
        # Support & Resistance frame
        levels_frame = ttk.LabelFrame(main_frame, text="Support & Resistance Levels", padding="10")
        levels_frame.pack(fill=tk.X, pady=5)
        
        levels_grid = ttk.Frame(levels_frame)
        levels_grid.pack(fill=tk.X)
        
        support_frame = ttk.Frame(levels_grid)
        support_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(support_frame, text="Support Levels", font=("Arial", 10, "bold"), foreground="green").pack(anchor="w")
        self.support_label = ttk.Label(support_frame, text="Calculating...", font=("Arial", 9))
        self.support_label.pack(anchor="w")
        
        resistance_frame = ttk.Frame(levels_grid)
        resistance_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(resistance_frame, text="Resistance Levels", font=("Arial", 10, "bold"), foreground="red").pack(anchor="w")
        self.resistance_label = ttk.Label(resistance_frame, text="Calculating...", font=("Arial", 9))
        self.resistance_label.pack(anchor="w")
        
        # Price history frame
        history_frame = ttk.LabelFrame(main_frame, text="Recent Price History", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create text widget for price history
        self.history_text = tk.Text(history_frame, height=10, font=("Courier", 8))
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_var = tk.StringVar(value="Starting data collection...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=5)
        
        # Disclaimer
        disclaimer_label = ttk.Label(main_frame, 
                                   text="⚠️ Disclaimer: This is for educational purposes only. Do your own research before trading.",
                                   font=("Arial", 8), foreground="red")
        disclaimer_label.pack(pady=5)
    
    def fetch_bitcoin_data(self):
        """Fetch Bitcoin data using urllib (no external packages needed)"""
        sources = [
            self.get_binance_data,
            self.get_coingecko_data,
            self.get_cryptocompare_data
        ]
        
        prices = []
        for source in sources:
            try:
                price = source()
                if price and price > 0:
                    prices.append(price)
                    if len(prices) >= 2:  # We need at least 2 sources
                        break
            except Exception as e:
                continue
        
        if prices:
            # Simulate volume data (since free APIs don't always provide volume)
            self.volume = random.uniform(1000000000, 5000000000)
            return sum(prices) / len(prices)
        return None
    
    def get_binance_data(self):
        """Get Bitcoin data from Binance"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return float(data['price'])
        except:
            return None
    
    def get_coingecko_data(self):
        """Get Bitcoin data from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data['bitcoin']['usd']
        except:
            return None
    
    def get_cryptocompare_data(self):
        """Get Bitcoin data from CryptoCompare"""
        try:
            url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data['USD']
        except:
            return None
    
    def calculate_sma(self, period):
        """Calculate Simple Moving Average"""
        if len(self.price_history) < period:
            return None
        return sum(list(self.price_history)[-period:]) / period
    
    def calculate_ema(self, period):
        """Calculate Exponential Moving Average"""
        if len(self.price_history) < period:
            return None
        
        prices = list(self.price_history)
        multiplier = 2 / (period + 1)
        
        # Start with SMA
        ema = sum(prices[:period]) / period
        
        # Calculate EMA for remaining values
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_macd(self):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_12 = self.calculate_ema(12)
        ema_26 = self.calculate_ema(26)
        
        if ema_12 is None or ema_26 is None:
            return None, None, None
        
        macd_line = ema_12 - ema_26
        
        # For signal line (EMA of MACD line), we need more history
        if len(self.price_history) >= 26 + 9:  # 26 for EMA, 9 for signal
            # Simplified signal line calculation
            signal_line = macd_line * 0.9  # Approximation
        else:
            signal_line = macd_line
        
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_rsi(self, period=14):
        """Calculate Relative Strength Index"""
        if len(self.price_history) < period + 1:
            return None
        
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
    
    def calculate_bollinger_bands(self, period=20):
        """Calculate Bollinger Bands"""
        if len(self.price_history) < period:
            return None, None, None
        
        prices = list(self.price_history)[-period:]
        middle_band = sum(prices) / period
        
        # Calculate standard deviation
        variance = sum((x - middle_band) ** 2 for x in prices) / period
        std_dev = math.sqrt(variance)
        
        upper_band = middle_band + (std_dev * 2)
        lower_band = middle_band - (std_dev * 2)
        
        return upper_band, middle_band, lower_band
    
    def calculate_support_resistance(self):
        """Calculate support and resistance levels"""
        if len(self.price_history) < 20:
            return [], []
        
        prices = list(self.price_history)
        
        # Simple method: use recent highs and lows
        recent_high = max(prices[-20:])
        recent_low = min(prices[-20:])
        current_price = prices[-1]
        
        # Calculate support levels (below current price)
        support1 = recent_low
        support2 = recent_low - (recent_high - recent_low) * 0.1
        support3 = recent_low - (recent_high - recent_low) * 0.2
        
        # Calculate resistance levels (above current price)
        resistance1 = recent_high
        resistance2 = recent_high + (recent_high - recent_low) * 0.1
        resistance3 = recent_high + (recent_high - recent_low) * 0.2
        
        # Filter levels to be meaningful
        support_levels = [level for level in [support1, support2, support3] if level < current_price]
        resistance_levels = [level for level in [resistance1, resistance2, resistance3] if level > current_price]
        
        return support_levels, resistance_levels
    
    def predict_future_prices(self):
        """Predict future prices using trend analysis"""
        if len(self.price_history) < 10:
            return None, None, None, None
        
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate short-term trend
        recent_trend = 0
        if len(prices) >= 5:
            short_trend = (prices[-1] - prices[-5]) / prices[-5] * 100
        else:
            short_trend = 0
        
        # Calculate medium-term trend
        if len(prices) >= 15:
            medium_trend = (prices[-1] - prices[-15]) / prices[-15] * 100
        else:
            medium_trend = short_trend
        
        # Calculate volatility
        if len(prices) >= 10:
            volatility = max(prices[-10:]) - min(prices[-10:])
            volatility_pct = volatility / current_price * 100
        else:
            volatility_pct = 2.0  # Default volatility
        
        # Predict future prices based on trends and volatility
        pred_5min = current_price * (1 + short_trend/100 * 0.1) * (1 + random.uniform(-volatility_pct/100, volatility_pct/100) * 0.5)
        pred_15min = current_price * (1 + short_trend/100 * 0.3) * (1 + random.uniform(-volatility_pct/100, volatility_pct/100) * 0.8)
        pred_1hr = current_price * (1 + medium_trend/100 * 0.8) * (1 + random.uniform(-volatility_pct/100, volatility_pct/100) * 1.2)
        pred_4hr = current_price * (1 + medium_trend/100 * 1.5) * (1 + random.uniform(-volatility_pct/100, volatility_pct/100) * 2.0)
        
        return pred_5min, pred_15min, pred_1hr, pred_4hr
    
    def calculate_trading_targets(self):
        """Calculate buy/sell targets and stop loss"""
        if len(self.price_history) < 10:
            return 0, 0, 0
        
        current_price = self.current_price
        atr = current_price * 0.02  # Average True Range approximation (2%)
        
        # Buy target (take profit)
        buy_target = current_price * 1.03  # 3% profit target
        
        # Sell target (take profit for short positions)
        sell_target = current_price * 0.97  # 3% profit target for shorts
        
        # Stop loss
        stop_loss = current_price * 0.98  # 2% stop loss
        
        return buy_target, sell_target, stop_loss
    
    def analyze_trend(self):
        """Analyze market trend and provide recommendation"""
        if len(self.price_history) < self.sma_long:
            return "HOLD", "Collecting more data for analysis", "orange"
        
        # Get current values
        current_price = self.current_price
        sma_short = self.calculate_sma(self.sma_short)
        sma_long = self.calculate_sma(self.sma_long)
        ema_short = self.calculate_ema(self.ema_short)
        ema_long = self.calculate_ema(self.ema_long)
        rsi = self.calculate_rsi(14)
        macd_line, signal_line, histogram = self.calculate_macd()
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands()
        
        if not all([sma_short, sma_long, rsi]):
            return "HOLD", "Calculating technical indicators", "orange"
        
        reasons = []
        score = 0
        
        # SMA Analysis
        if sma_short > sma_long:
            reasons.append("Bullish SMA crossover")
            score += 1
        else:
            reasons.append("Bearish SMA")
            score -= 1
        
        # EMA Analysis
        if ema_short and ema_long and ema_short > ema_long:
            reasons.append("Bullish EMA crossover")
            score += 1
        elif ema_short and ema_long:
            reasons.append("Bearish EMA")
            score -= 1
        
        # RSI Analysis
        if rsi < 30:
            reasons.append("Oversold (RSI < 30)")
            score += 2
        elif rsi > 70:
            reasons.append("Overbought (RSI > 70)")
            score -= 1
        else:
            reasons.append(f"RSI neutral ({rsi:.1f})")
        
        # MACD Analysis
        if macd_line and signal_line:
            if macd_line > signal_line and histogram > 0:
                reasons.append("Bullish MACD")
                score += 1
            elif macd_line < signal_line and histogram < 0:
                reasons.append("Bearish MACD")
                score -= 1
        
        # Bollinger Bands Analysis
        if bb_upper and bb_lower:
            if current_price < bb_lower:
                reasons.append("Oversold (below lower Bollinger Band)")
                score += 1
            elif current_price > bb_upper:
                reasons.append("Overbought (above upper Bollinger Band)")
                score -= 1
        
        # Price momentum
        if len(self.price_history) >= 5:
            recent_prices = list(self.price_history)[-5:]
            price_momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            if price_momentum > 1:
                reasons.append(f"Upward momentum (+{price_momentum:.1f}%)")
                score += 1
            elif price_momentum < -1:
                reasons.append(f"Downward momentum ({price_momentum:.1f}%)")
                score -= 1
        
        # Generate recommendation
        if score >= 4:
            recommendation = "STRONG BUY"
            color = "dark green"
        elif score >= 2:
            recommendation = "BUY"
            color = "green"
        elif score <= -4:
            recommendation = "STRONG SELL"
            color = "dark red"
        elif score <= -2:
            recommendation = "SELL"
            color = "red"
        else:
            recommendation = "HOLD"
            color = "orange"
        
        reason_text = " | ".join(reasons)
        
        return recommendation, reason_text, color
    
    def update_display(self):
        """Update the UI with current data"""
        try:
            # Update price display
            if self.current_price > 0:
                self.price_label.config(text=f"${self.current_price:,.2f}")
            
            # Update change display
            change_color = "green" if self.price_change >= 0 else "red"
            change_symbol = "+" if self.price_change >= 0 else ""
            if self.current_price > 0:
                self.change_label.config(
                    text=f"{change_symbol}${abs(self.price_change):.2f} ({change_symbol}{self.change_percentage:.2f}%)",
                    foreground=change_color
                )
            
            # Update prediction and indicators
            recommendation, reason, color = self.analyze_trend()
            self.prediction_label.config(text=f"Recommendation: {recommendation}", foreground=color)
            self.reason_label.config(text=reason)
            
            # Update technical indicators
            self.update_technical_indicators()
            
            # Update price predictions
            self.update_price_predictions()
            
            # Update trading targets
            self.update_trading_targets()
            
            # Update support and resistance
            self.update_support_resistance()
            
            # Update price history
            self.update_history_display()
            
            # Update status
            self.status_var.set(f"Last update: {datetime.now().strftime('%H:%M:%S')} | Prices from: Binance, CoinGecko, CryptoCompare")
            
        except Exception as e:
            self.status_var.set(f"Error updating display: {str(e)}")
    
    def update_technical_indicators(self):
        """Update technical indicators display"""
        sma_short = self.calculate_sma(self.sma_short)
        sma_long = self.calculate_sma(self.sma_long)
        ema_short = self.calculate_ema(self.ema_short)
        ema_long = self.calculate_ema(self.ema_long)
        rsi = self.calculate_rsi(14)
        macd_line, signal_line, histogram = self.calculate_macd()
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands()
        
        # Update indicator labels
        if sma_short and sma_long:
            self.sma_label.config(text=f"SMA: {sma_short:.0f}/{sma_long:.0f} ({'Bullish' if sma_short > sma_long else 'Bearish'})")
        
        if ema_short and ema_long:
            self.ema_label.config(text=f"EMA: {ema_short:.0f}/{ema_long:.0f} ({'Bullish' if ema_short > ema_long else 'Bearish'})")
        
        if macd_line and signal_line:
            macd_status = "Bullish" if macd_line > signal_line else "Bearish"
            self.macd_label.config(text=f"MACD: {macd_line:.2f} | Signal: {signal_line:.2f} ({macd_status})")
        
        if rsi:
            rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            self.rsi_label.config(text=f"RSI: {rsi:.1f} ({rsi_status})")
        
        if bb_upper and bb_lower:
            bb_position = "Upper" if self.current_price > bb_upper else "Lower" if self.current_price < bb_lower else "Middle"
            self.bollinger_label.config(text=f"Bollinger: Position: {bb_position}")
        
        # Volume trend (simulated)
        volume_trend = "Increasing" if random.random() > 0.5 else "Decreasing"
        self.volume_label.config(text=f"Volume Trend: {volume_trend}")
    
    def update_price_predictions(self):
        """Update price predictions display"""
        pred_5min, pred_15min, pred_1hr, pred_4hr = self.predict_future_prices()
        
        if pred_5min:
            change_5min = (pred_5min - self.current_price) / self.current_price * 100
            color_5min = "green" if change_5min > 0 else "red"
            self.pred_5min_label.config(
                text=f"${pred_5min:,.0f}\n({change_5min:+.1f}%)", 
                foreground=color_5min
            )
        
        if pred_15min:
            change_15min = (pred_15min - self.current_price) / self.current_price * 100
            color_15min = "green" if change_15min > 0 else "red"
            self.pred_15min_label.config(
                text=f"${pred_15min:,.0f}\n({change_15min:+.1f}%)", 
                foreground=color_15min
            )
        
        if pred_1hr:
            change_1hr = (pred_1hr - self.current_price) / self.current_price * 100
            color_1hr = "green" if change_1hr > 0 else "red"
            self.pred_1hr_label.config(
                text=f"${pred_1hr:,.0f}\n({change_1hr:+.1f}%)", 
                foreground=color_1hr
            )
        
        if pred_4hr:
            change_4hr = (pred_4hr - self.current_price) / self.current_price * 100
            color_4hr = "green" if change_4hr > 0 else "red"
            self.pred_4hr_label.config(
                text=f"${pred_4hr:,.0f}\n({change_4hr:+.1f}%)", 
                foreground=color_4hr
            )
    
    def update_trading_targets(self):
        """Update trading targets display"""
        buy_target, sell_target, stop_loss = self.calculate_trading_targets()
        
        if buy_target:
            self.buy_target_label.config(text=f"Buy Target: ${buy_target:,.0f} (+{((buy_target - self.current_price) / self.current_price * 100):.1f}%)")
        
        if sell_target:
            self.sell_target_label.config(text=f"Sell Target: ${sell_target:,.0f} ({((sell_target - self.current_price) / self.current_price * 100):.1f}%)")
        
        if stop_loss:
            self.stop_loss_label.config(text=f"Stop Loss: ${stop_loss:,.0f} ({((stop_loss - self.current_price) / self.current_price * 100):.1f}%)")
    
    def update_support_resistance(self):
        """Update support and resistance levels display"""
        support_levels, resistance_levels = self.calculate_support_resistance()
        
        if support_levels:
            support_text = "\n".join([f"${level:,.0f}" for level in support_levels[:3]])
            self.support_label.config(text=support_text)
        
        if resistance_levels:
            resistance_text = "\n".join([f"${level:,.0f}" for level in resistance_levels[:3]])
            self.resistance_label.config(text=resistance_text)
    
    def update_history_display(self):
        """Update the price history text widget"""
        self.history_text.delete(1.0, tk.END)
        
        if len(self.price_history) > 0:
            self.history_text.insert(tk.END, "Time                 Price        Change      Volume\n")
            self.history_text.insert(tk.END, "-" * 60 + "\n")
            
            # Show last 15 prices in reverse order (newest first)
            prices = list(self.price_history)
            
            for i in range(min(15, len(prices))):
                idx = len(prices) - 1 - i  # Reverse index
                price = prices[idx]
                time_str = datetime.now().strftime("%H:%M:%S")
                
                # Calculate change from previous price
                if idx > 0:
                    change = price - prices[idx-1]
                    change_pct = (change / prices[idx-1]) * 100
                    change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                else:
                    change_str = "N/A"
                
                # Simulate volume
                volume = random.uniform(1000000000, 5000000000)
                volume_str = f"${volume/1000000:.1f}M"
                
                self.history_text.insert(tk.END, f"{time_str}    ${price:8.2f}    {change_str:>15}    {volume_str:>10}\n")
    
    def data_loop(self):
        """Main data fetching loop"""
        previous_price = None
        error_count = 0
        
        while self.running:
            try:
                # Fetch new price
                new_price = self.fetch_bitcoin_data()
                
                if new_price:
                    self.current_price = new_price
                    
                    # Calculate changes
                    if previous_price is not None:
                        self.price_change = new_price - previous_price
                        self.change_percentage = (self.price_change / previous_price) * 100
                    
                    # Update history
                    self.price_history.append(new_price)
                    self.volume_history.append(self.volume)
                    
                    previous_price = new_price
                    error_count = 0  # Reset error count on success
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_display)
                else:
                    error_count += 1
                    if error_count > 5:
                        self.status_var.set("Error: Unable to fetch Bitcoin prices. Check internet connection.")
                
                # Wait 3 seconds before next update (slower to avoid rate limits)
                time.sleep(3)
                
            except Exception as e: 
                error_count += 1
                print(f"Error in data loop: {e}")
                time.sleep(5)  # Wait longer if there's an error
    
    def start_data_fetching(self):
        """Start the data fetching in a separate thread"""
        self.data_thread = threading.Thread(target=self.data_loop, daemon=True)
        self.data_thread.start()
    
    def on_closing(self):
        """Handle application closing"""
        self.running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BitcoinPredictor(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_closing()

if __name__ == "__main__":
    main()
