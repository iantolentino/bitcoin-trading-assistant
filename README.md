# Bitcoin Trading Assistant 🤖📈

A Flask-based web application that provides AI-powered Bitcoin trading signals using technical analysis. This tool analyzes market data to generate buy/sell/hold recommendations with confidence scores.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

- **Technical Analysis**: RSI, Moving Averages (SMA, EMA), MACD calculations
- **Smart Signals**: AI-powered buy/sell/hold recommendations
- **Market Sentiment**: Fear & Greed index simulation
- **Real-time Data**: Fetches live Bitcoin prices from CoinGecko API
- **REST API**: JSON endpoints for programmatic access
- **Responsive Design**: Works on desktop and mobile devices
- **Educational Focus**: Clear disclaimers and risk warnings

## 📊 Technical Indicators

| Indicator | Description | Signal Type |
|-----------|-------------|-------------|
| RSI (14) | Relative Strength Index | Overbought/Oversold |
| SMA 20/50 | Simple Moving Average | Trend Direction |
| EMA 12/26 | Exponential Moving Average | Momentum |
| MACD | Moving Average Convergence Divergence | Trend Changes |
| Market Sentiment | Fear & Greed Index | Market Psychology |

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download
```bash
# Option 1: Download the single file
wget https://your-repo.com/bitcoin-trading-assistant/app.py

# Option 2: Clone repository (if available)
git clone https://github.com/your-username/bitcoin-trading-assistant.git
cd bitcoin-trading-assistant
```

### Step 2: Install Dependencies
```bash
pip install flask requests pandas numpy
```

### Step 3: Run the Application
```bash
python app.py
```

## 🎯 Usage

### Web Interface
1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open your browser** to:
   ```
   http://localhost:5000
   ```

3. **Configure analysis**:
   - Select time frame (30, 90, or 180 days)
   - Choose analysis type
   - Click "Analyze Bitcoin Now"

4. **Review results**:
   - Trading recommendation (BUY/SELL/HOLD)
   - Confidence percentage
   - Technical indicators
   - Market sentiment
   - Detailed trading signals

### API Endpoints

#### Get Analysis (JSON)
```bash
curl http://localhost:5000/api/analysis
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00",
  "analysis": {
    "recommendation": "BUY",
    "confidence": 85,
    "current_price": 45230.50,
    "rsi": 45.2,
    "signals": ["RSI indicates OVERSOLD - STRONG BUY signal", ...]
  },
  "sentiment": {
    "sentiment": "Greed",
    "score": 65,
    "color": "warning"
  }
}
```

#### Health Check
```bash
curl http://localhost:5000/health
```

## 📈 How It Works

### Data Flow
1. **Data Collection**: Fetches Bitcoin price data from CoinGecko API
2. **Technical Analysis**: Calculates multiple indicators manually
3. **Signal Generation**: Combines indicators for robust signals
4. **Recommendation**: Provides clear trading advice with confidence scores

### Algorithm
```python
# Sample calculation logic
RSI < 30 → Oversold → BUY signal
RSI > 70 → Overbought → SELL signal
SMA_20 > SMA_50 → Golden Cross → BUY signal
SMA_20 < SMA_50 → Death Cross → SELL signal
MACD > 0 → Bullish momentum → BUY signal
```

## 🏗 Project Structure

```
bitcoin-trading-assistant/
├── app.py                 # Main application file
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

### Key Components
- **BitcoinTradingAssistant**: Main analysis class
- **Flask Routes**: Web interface and API endpoints
- **HTML Templates**: Embedded in the Python file
- **Technical Calculators**: Manual indicator calculations

## 🔧 Configuration

### Time Frames
- **30 days**: Short-term analysis
- **90 days**: Medium-term trends  
- **180 days**: Long-term perspective

### Analysis Types
- **Technical Analysis**: Multiple indicator combination
- **Trend Analysis**: Price movement patterns

## ⚠️ Important Disclaimer

**🚨 EDUCATIONAL PURPOSE ONLY**

This application is designed for **educational and informational purposes only**. It is **NOT financial advice** and should **NOT** be used for actual trading decisions.

### Risks Include:
- Cryptocurrency volatility
- Market unpredictability
- Technical analysis limitations
- Potential financial losses

**Always:**
- Do your own research
- Consult financial advisors
- Understand the risks
- Never invest more than you can afford to lose

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
# Or use different port
python app.py --port 5001
```

**API connection failed:**
- Application automatically uses sample data
- Check internet connection
- Verify CoinGecko API status

**Import errors:**
```bash
# Reinstall dependencies
pip install --force-reinstall flask requests pandas numpy
```

### Debug Mode
```bash
# Enable debug output
python app.py
# Check console for detailed logs
```

## 📊 Sample Output

### Web Interface
```
🎯 RECOMMENDATION: BUY
📊 Confidence: 85%
💰 Current Price: $45,230.50

📈 Technical Indicators:
- RSI: 45.2 (Neutral)
- SMA 20: $44,100
- SMA 50: $43,500

🎭 Market Sentiment: Greed (65/100)
```

### Trading Signals
- ✅ RSI indicates OVERSOLD - STRONG BUY signal
- ✅ Golden Cross pattern - BULLISH BUY signal  
- ✅ MACD positive - BULLISH momentum
- 📈 Short-term trend: UP

## 🔮 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Additional technical indicators
- [ ] Portfolio tracking
- [ ] Email/SMS alerts
- [ ] Historical performance analysis
- [ ] Multiple cryptocurrency support
- [ ] Advanced machine learning models

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CoinGecko** for providing free cryptocurrency API
- **Flask** community for the excellent web framework
- **Technical Analysis** principles from traditional finance

---

**💡 Remember:** This tool is for learning purposes. Always verify signals with multiple sources and practice risk management in real trading.
