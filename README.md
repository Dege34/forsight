# ForSight 📈

**AI-Powered BIST Analysis & Prediction Platform**

ForSight is a state-of-the-art financial analysis tool designed specifically for the Borsa Istanbul (BIST) market. Leveraging advanced machine learning models and a vast database spanning over 28 years (1997-2025), ForSight provides investors with data-driven insights, price predictions, and comprehensive technical analysis.

<img width="1882" height="898" alt="Ekran görüntüsü 2025-11-29 032411" src="https://github.com/Dege34/forsight/blob/main/asset/header1.png" />


## 🚀 Key Features

### 🤖 AI-Powered Multi-Model Prediction
ForSight employs an ensemble of powerful machine learning algorithms to forecast stock prices:
*   **Multiple Models:** Linear Regression, Random Forest, XGBoost, and Gradient Boosting.
*   **Performance Tracking:** Real-time comparison of model accuracy (RMSE, R²) to select the best predictor for each stock.
*   **Future Insights:** 30-day price predictions with expected percentage changes.

#### 🧠 Model Algorithms & Mathematical Foundations

This project utilizes several machine learning algorithms to predict future stock movements based on historical BIST data. Below are the mathematical foundations and working principles of each model used.

#### 1. Linear Regression
This is the baseline model establishing a linear relationship between the independent variables (technical indicators) and the dependent variable (price).

**Hypothesis Function:**
$$h_\theta(x) = \theta_0 + \theta_1 x_1 + \theta_2 x_2 + ... + \theta_n x_n$$

Where:
* $y$: Predicted price.
* $x$: Feature vector (RSI, MACD, Volume, etc.).
* $\theta$: Coefficients (weights) learned by the model.

**Cost Function (MSE):**
The model aims to minimize the Mean Squared Error:
$$J(\theta) = \frac{1}{m} \sum_{i=1}^{m} (h_\theta(x^{(i)}) - y^{(i)})^2$$

#### 2. Random Forest Regression
An ensemble learning method that operates by constructing a multitude of decision trees at training time. It reduces variance through **Bagging** (Bootstrap Aggregating).

**Prediction:**
For an input $x$, the prediction is the average of the outputs from $K$ individual trees:

$$\hat{y} = \frac{1}{K} \sum_{k=1}^{K} T_k(x)$$

Where:
* $T_k(x)$: Output of the $k$-th decision tree.
* $K$: Total number of trees in the forest.

**Splitting Criterion:**
Trees are grown by selecting splits that minimize the Sum of Squared Errors (SSE):
$$SSE = \sum_{i \in S_1} (y_i - \bar{y}_1)^2 + \sum_{i \in S_2} (y_i - \bar{y}_2)^2$$

#### 3. Gradient Boosting Machines (GBM)
A boosting technique that builds the model in a stage-wise fashion. It constructs new weak learners (trees) to correct the errors (residuals) made by previous models.

**Additive Model:**
$$F_m(x) = F_{m-1}(x) + \nu \cdot h_m(x)$$

Where:
* $F_m(x)$: Current model at stage $m$.
* $h_m(x)$: New weak learner trained to predict residuals.
* $\nu$: Learning rate ($0 < \nu \le 1$).

**Pseudo-Residuals (Gradient):**
The model updates in the direction of the negative gradient of the loss function $L$:
$$r_{im} = -\left[ \frac{\partial L(y_i, F(x_i))}{\partial F(x_i)} \right]_{F(x) = F_{m-1}(x)}$$

#### 4. XGBoost (Extreme Gradient Boosting)
An optimized distributed gradient boosting library. Key differences from standard GBM include the use of **Taylor Series Expansion** (2nd order derivative) and built-in **Regularization** to prevent overfitting.

**Objective Function:**
$$Obj^{(t)} = \sum_{i=1}^{n} L(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)) + \Omega(f_t)$$

**Taylor Expansion Approximation:**
$$Obj^{(t)} \approx \sum_{i=1}^{n} [L(y_i, \hat{y}_i^{(t-1)}) + g_i f_t(x_i) + \frac{1}{2}h_i f_t^2(x_i)] + \Omega(f_t)$$

Where:
* $g_i$: First derivative (Gradient) of the loss function.
* $h_i$: Second derivative (Hessian) of the loss function.
* $\Omega(f_t)$: Regularization term.

**Regularization ($\Omega$):**
Controls model complexity:
$$\Omega(f) = \gamma T + \frac{1}{2}\lambda ||w||^2$$
*(T: Number of leaves, w: Leaf scores)*

**Optimal Leaf Weight:**
$$w^*_j = - \frac{\sum_{i \in I_j} g_i}{\sum_{i \in I_j} h_i + \lambda}$$

---

### 📊 Comprehensive Symbol Analysis
*   **Deep History:** Access to daily price data, volume, and returns dating back to 1997.
*   **Key Metrics:** Instant visualization of Volatility (Standard Deviation), Sharpe Ratio, and Average Daily Returns.
*   **Interactive Charts:** Zoomable charts for normalized price movements and comparative analysis.
---
### 📈 Technical Indicators & Signals
*   **Smart Signals:** Automated "Buy" and "Sell" signals based on Moving Average Crossovers (e.g., MA20 vs MA50).
*   **Visual Indicators:** Clear visualization of trends and momentum directly on the price chart.
---
### 🎨 Modern & Responsive Design
*   **Dynamic Theming:** Fully supported Dark and Light modes for optimal readability.
*   **Glassmorphism UI:** A sleek, modern interface designed for professional use.
---
## 🛠️ Tech Stack

*   **Frontend:** React.js, Vite, Modern CSS (Variables & Animations)
*   **Backend:** Python (Flask/FastAPI), Pandas, NumPy
*   **Machine Learning:** Scikit-Learn, XGBoost
*   **Data:** SQLite (Historical BIST Data)
---
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
| <img width="1882" height="898" alt="Ekran görüntüsü 2025-11-29 032411" src="https://github.com/Dege34/forsight/blob/main/asset/header1.png" /> | <img width="1882" height="898" alt="Ekran görüntüsü 2025-11-29 032411" src="https://github.com/Dege34/forsight/blob/main/asset/header3.png" /> |

| Symbol Search | Technical Charts |
|:---:|:---:|
| <img width="1882" height="898" alt="Ekran görüntüsü 2025-11-29 032411" src="https://github.com/Dege34/forsight/blob/main/asset/header2.png" /> | <img width="1882" height="898" alt="Ekran görüntüsü 2025-11-29 032411" src="https://github.com/Dege34/forsight/blob/main/asset/header4.png" /> |

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Dege34/ForSight/issues).

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
