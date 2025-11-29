# ForSight 📈

**AI-Powered BIST Analysis & Prediction Platform**

ForSight is a state-of-the-art financial analysis tool designed specifically for the Borsa Istanbul (BIST) market. Leveraging advanced machine learning models and a vast database spanning over 28 years (1997-2025), ForSight provides investors with data-driven insights, price predictions, and comprehensive technical analysis.

<img width="1882" height="898" alt="Ekran görüntüsü 2025-11-29 032411" src="https://github.com/Dege34/forsight/blob/main/asset/header1.png" />

*(Replace this link with your actual screenshot)*

## 🚀 Key Features

### 🤖 AI-Powered Multi-Model Prediction
ForSight employs an ensemble of powerful machine learning algorithms to forecast stock prices:
*   **Multiple Models:** Linear Regression, Random Forest, XGBoost, and Gradient Boosting.
*   **Performance Tracking:** Real-time comparison of model accuracy (RMSE, R²) to select the best predictor for each stock.
*   **Future Insights:** 30-day price predictions with expected percentage changes.

### 📊 Comprehensive Symbol Analysis
*   **Deep History:** Access to daily price data, volume, and returns dating back to 1997.
*   **Key Metrics:** Instant visualization of Volatility (Standard Deviation), Sharpe Ratio, and Average Daily Returns.
*   **Interactive Charts:** Zoomable charts for normalized price movements and comparative analysis.

### 📈 Technical Indicators & Signals
*   **Smart Signals:** Automated "Buy" and "Sell" signals based on Moving Average Crossovers (e.g., MA20 vs MA50).
*   **Visual Indicators:** Clear visualization of trends and momentum directly on the price chart.

### 🎨 Modern & Responsive Design
*   **Dynamic Theming:** Fully supported Dark and Light modes for optimal readability.
*   **Glassmorphism UI:** A sleek, modern interface designed for professional use.

## 🛠️ Tech Stack

*   **Frontend:** React.js, Vite, Modern CSS (Variables & Animations)
*   **Backend:** Python (Flask/FastAPI), Pandas, NumPy
*   **Machine Learning:** Scikit-Learn, XGBoost
*   **Data:** SQLite (Historical BIST Data)

## 📦 Installation & Setup

### Prerequisites
*   Python 3.8+
*   Node.js & npm

### 1. Clone the Repository
```bash
git clone https://github.com/Dege34/ForSight.git
cd ForSight
```

### 2. Backend Setup
Navigate to the root directory and install Python dependencies (create a virtual environment recommended):
```bash
# Install dependencies (ensure you have a requirements.txt, or install manually)
pip install flask pandas scikit-learn xgboost

# Run the API server
python api.py
```

### 3. Frontend Setup
Navigate to the web directory:
```bash
cd web

# Install Node modules
npm install

# Start the development server
npm run dev
```

## 📸 Gallery

| Landing Page | AI Predictions |
|:---:|:---:|
| ![Landing](https://via.placeholder.com/400x200?text=Landing+Page) | ![Predictions](https://via.placeholder.com/400x200?text=AI+Predictions) |

| Symbol Search | Technical Charts |
|:---:|:---:|
| ![Search](https://via.placeholder.com/400x200?text=Symbol+Search) | ![Charts](https://via.placeholder.com/400x200?text=Technical+Charts) |

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Dege34/ForSight/issues).

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
