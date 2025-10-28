import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
from datetime import datetime
from collections import deque
import urllib.request
import urllib.error  

class BitcoinPredictor:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Real-Time Predictor")
        self.root.geometry("900x600")
        
        # Center the window
        self.center_window(900, 600)
        
        # Data storage
        self.price_history = deque(maxlen=50)
        self.current_price = 0
        self.price_change = 0
        self.change_percentage = 0
        
        # Prediction parameters
        self.sma_short = 10
        self.sma_long = 20
        
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
        title_label = ttk.Label(main_frame, text="₿ Bitcoin Trading Assistant", 
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
        
        # Prediction frame
        pred_frame = ttk.LabelFrame(main_frame, text="Trading Recommendation", padding="10")
        pred_frame.pack(fill=tk.X, pady=5)
        
        self.prediction_label = ttk.Label(pred_frame, text="Analyzing market data...", 
                                        font=("Arial", 14, "bold"))
        self.prediction_label.pack()
        
        self.reason_label = ttk.Label(pred_frame, text="", font=("Arial", 10), 
                                     wraplength=800, justify=tk.CENTER)
        self.reason_label.pack(pady=5)
        
        # Technical indicators frame
        tech_frame = ttk.LabelFrame(main_frame, text="Technical Indicators", padding="10")
        tech_frame.pack(fill=tk.X, pady=5)
        
        self.indicators_label = ttk.Label(tech_frame, text="Calculating indicators...", 
                                        font=("Arial", 9))
        self.indicators_label.pack()
        
        # Price history frame
        history_frame = ttk.LabelFrame(main_frame, text="Recent Price History", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create text widget for price history
        self.history_text = tk.Text(history_frame, height=8, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        self.history_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
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
    
    def analyze_trend(self):
        """Analyze market trend and provide recommendation"""
        if len(self.price_history) < self.sma_long:
            return "HOLD", "Collecting more data for analysis", "orange", "Waiting for sufficient price history"
        
        # Get current values
        current_price = self.current_price
        sma_short = self.calculate_sma(self.sma_short)
        sma_long = self.calculate_sma(self.sma_long)
        rsi = self.calculate_rsi(14)
        
        if not all([sma_short, sma_long, rsi]):
            return "HOLD", "Calculating technical indicators", "orange", "Insufficient data for full analysis"
        
        reasons = []
        score = 0
        
        # SMA Analysis
        if sma_short > sma_long:
            reasons.append("Bullish trend (SMA crossover)")
            score += 1
        else:
            reasons.append("Bearish trend")
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
        
        # Price position relative to SMA
        if current_price > sma_long:
            reasons.append("Price above long-term average")
            score += 1
        else:
            reasons.append("Price below long-term average")
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
        if score >= 3:
            recommendation = "STRONG BUY"
            color = "dark green"
        elif score >= 2:
            recommendation = "BUY"
            color = "green"
        elif score <= -3:
            recommendation = "STRONG SELL"
            color = "dark red"
        elif score <= -2:
            recommendation = "SELL"
            color = "red"
        else:
            recommendation = "HOLD"
            color = "orange"
        
        reason_text = " | ".join(reasons)
        
        # Technical indicators text
        indicators_text = f"SMA-{self.sma_short}: ${sma_short:.2f} | SMA-{self.sma_long}: ${sma_long:.2f} | RSI: {rsi:.1f}"
        
        return recommendation, reason_text, color, indicators_text
    
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
            
            # Update prediction
            recommendation, reason, color, indicators = self.analyze_trend()
            self.prediction_label.config(text=f"Recommendation: {recommendation}", foreground=color)
            self.reason_label.config(text=reason)
            self.indicators_label.config(text=indicators)
            
            # Update price history
            self.update_history_display()
            
            # Update status
            self.status_var.set(f"Last update: {datetime.now().strftime('%H:%M:%S')} | Prices from: Binance, CoinGecko, CryptoCompare")
            
        except Exception as e:
            self.status_var.set(f"Error updating display: {str(e)}")
    
    def update_history_display(self):
        """Update the price history text widget"""
        self.history_text.delete(1.0, tk.END)
        
        if len(self.price_history) > 0:
            self.history_text.insert(tk.END, "Time                 Price        Change\n")
            self.history_text.insert(tk.END, "-" * 50 + "\n")
            
            # Show last 20 prices in reverse order (newest first)
            prices = list(self.price_history)
            times = [datetime.now() for _ in range(len(prices))]  # Simplified time tracking
            
            for i in range(min(20, len(prices))):
                idx = len(prices) - 1 - i  # Reverse index
                price = prices[idx]
                time_str = times[idx].strftime("%H:%M:%S") if idx < len(times) else "N/A"
                
                # Calculate change from previous price
                if idx > 0:
                    change = price - prices[idx-1]
                    change_pct = (change / prices[idx-1]) * 100
                    change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                else:
                    change_str = "N/A"
                
                self.history_text.insert(tk.END, f"{time_str}    ${price:8.2f}    {change_str}\n")
    
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
                    
                    previous_price = new_price
                    error_count = 0  # Reset error count on success
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_display)
                else:
                    error_count += 1
                    if error_count > 5:
                        self.status_var.set("Error: Unable to fetch Bitcoin prices. Check internet connection.")
                
                # Wait 2 seconds before next update (slower to avoid rate limits)
                time.sleep(2)
                
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

