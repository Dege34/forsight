from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. Install with: pip install xgboost")
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

DB_PATH = "bist_model_ready.db"

# Actual column names from database
ACTUAL_COLUMNS = [
    'symbol', 'date', 'close', 'weighted_average_try', 'low', 'high', 'volume_try',
    'bist', 'usd_kur_price', 'close_usd', 'relative_to_index', 'volume_usd',
    'market_cap_try', 'market_cap_usd', 'market_cap_tl_halka_acik', 'market_cap_usd_halka_acik',
    'volume', 'min_usd', 'max_usd', 'weighted_average_usd', 'pct_change',
    'rsi_14', 'macd_12_26_9', 'macdh_12_26_9', 'macds_12_26_9', 'sma_50', 'sma_200',
    'bbl_20_2.0_2.0', 'bbm_20_2.0_2.0', 'bbu_20_2.0_2.0', 'bbb_20_2.0_2.0', 'bbp_20_2.0_2.0',
    'brent_oil', 'sp500', 'vix', 'xbank_xusin_ratio', 'atr', 'obv', 'mfi'
]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def safe_column_name(col):
    """Wrap column names with special characters in quotes"""
    if '.' in col or '-' in col:
        return f'"{col}"'
    return col

def train_and_predict_model(symbol, days_ahead=30):
    """Train multiple ML models and return the best prediction"""
    conn = get_db_connection()
    
    # Build query with properly quoted column names
    columns_str = ', '.join([safe_column_name(col) for col in ACTUAL_COLUMNS])
    query = f"""
    SELECT {columns_str}
    FROM model_data 
    WHERE symbol = ? 
    ORDER BY date ASC
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(symbol,))
        conn.close()
    except Exception as e:
        conn.close()
        print(f"Error fetching data for {symbol}: {e}")
        return None
    
    if len(df) < 200:
        return None
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Feature engineering
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    df['volatility_20'] = df['returns'].rolling(window=20).std()
    df['volatility_50'] = df['returns'].rolling(window=50).std()
    df['momentum_10'] = df['close'] - df['close'].shift(10)
    df['momentum_20'] = df['close'] - df['close'].shift(20)
    
    # Target: Future price
    df['target'] = df['close'].shift(-days_ahead)
    
    # Drop rows with NaN
    df = df.dropna()
    
    if len(df) < 100:
        return None
    
    # Select numeric features
    feature_cols = [col for col in df.columns if col not in ['symbol', 'date', 'target']]
    feature_cols = [col for col in feature_cols if df[col].dtype in ['float64', 'int64']]
    
    # Remove columns with too many NaN or zero variance
    valid_features = []
    for col in feature_cols:
        if df[col].notna().sum() > len(df) * 0.5 and df[col].std() > 0:
            valid_features.append(col)
    
    if len(valid_features) < 5:
        return None
    
    X = df[valid_features].fillna(0)
    y = df['target']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # Standardize
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
        'Linear Regression': LinearRegression()
    }
    
    # Add XGBoost if available
    if XGBOOST_AVAILABLE:
        models['XGBoost'] = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
    
    best_model = None
    best_model_name = None
    best_r2 = -np.inf
    model_results = {}
    
    for name, model in models.items():
        try:
            model.fit(X_train_scaled, y_train)
            y_pred_test = model.predict(X_test_scaled)
            
            test_r2 = r2_score(y_test, y_pred_test)
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=min(5, len(X_train)//20), scoring='r2')
            
            model_results[name] = {
                'test_r2': float(test_r2),
                'cv_r2': float(cv_scores.mean()),
                'rmse': float(test_rmse),
                'mae': float(test_mae),
                'accuracy': float(max(0, min(100, test_r2 * 100)))
            }
            
            if test_r2 > best_r2:
                best_r2 = test_r2
                best_model = model
                best_model_name = name
        except Exception as e:
            print(f"Error training {name}: {e}")
            continue
    
    if best_model is None:
        return None
    
    # Make prediction
    last_features = X.iloc[-1:].values
    last_features_scaled = scaler.transform(last_features)
    future_prediction = best_model.predict(last_features_scaled)[0]
    
    current_price = float(df['close'].iloc[-1])
    predicted_change = ((future_prediction - current_price) / current_price) * 100
    
    # Feature importance
    feature_importance = {}
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        indices = np.argsort(importances)[::-1][:10]
        feature_importance = {valid_features[i]: float(importances[i]) for i in indices}
    
    # Correlations
    correlations = df[valid_features + ['target']].corr()['target'].drop('target')
    top_correlations = correlations.abs().sort_values(ascending=False)[:10]
    
    return {
        'current_price': current_price,
        'predicted_price': float(future_prediction),
        'predicted_change_percent': float(predicted_change),
        'best_model': best_model_name,
        'model_metrics': model_results[best_model_name],
        'all_models': model_results,
        'accuracy': float(max(0, min(100, best_r2 * 100))),
        'confidence': 'High' if best_r2 > 0.7 else 'Medium' if best_r2 > 0.5 else 'Low',
        'prediction_basis': {
            'model': best_model_name,
            'features_used': len(valid_features),
            'feature_names': valid_features[:20],
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'cross_validation_folds': min(5, len(X_train)//20),
            'top_features': feature_importance,
            'top_correlations': {k: float(v) for k, v in top_correlations.items()}
        },
        'days_ahead': days_ahead
    }

@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    """Get all available symbols"""
    conn = get_db_connection()
    query = "SELECT DISTINCT symbol FROM model_data ORDER BY symbol"
    symbols = [row['symbol'] for row in conn.execute(query).fetchall()]
    conn.close()
    return jsonify(symbols)

@app.route('/api/symbol/<symbol>', methods=['GET'])
def get_symbol_data(symbol):
    """Get comprehensive data for a specific symbol"""
    start_date = request.args.get('start_date', '1997-01-01')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    
    # Build query with properly quoted column names
    columns_str = ', '.join([safe_column_name(col) for col in ACTUAL_COLUMNS])
    query = f"""
    SELECT {columns_str}
    FROM model_data 
    WHERE symbol = ? AND date BETWEEN ? AND ?
    ORDER BY date ASC
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        conn.close()
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    if df.empty:
        return jsonify({'error': 'Symbol not found or no data available'}), 404
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate metrics
    df['returns'] = df['close'].pct_change()
    df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()
    df['ma_200'] = df['close'].rolling(window=200).mean()
    df['volatility'] = df['returns'].rolling(window=20).std()
    df['z_score'] = (df['close'] - df['close'].rolling(window=20).mean()) / df['close'].rolling(window=20).std()
    df['normalized_price'] = (df['close'] - df['close'].min()) / (df['close'].max() - df['close'].min())
    df['signal'] = 0
    df.loc[df['ma_20'] > df['ma_50'], 'signal'] = 1
    df.loc[df['ma_20'] < df['ma_50'], 'signal'] = -1
    
    # Add open if not exists
    if 'open' not in df.columns:
        df['open'] = df['close']
    
    # Statistics
    stats_data = {
        'total_records': len(df),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d'),
            'end': df['date'].max().strftime('%Y-%m-%d')
        },
        'price_stats': {
            'current': float(df['close'].iloc[-1]),
            'min': float(df['close'].min()),
            'max': float(df['close'].max()),
            'mean': float(df['close'].mean()),
            'std': float(df['close'].std())
        },
        'returns_stats': {
            'total_return': float(df['cumulative_returns'].iloc[-1] * 100) if len(df) > 1 else 0,
            'avg_daily_return': float(df['returns'].mean() * 100) if len(df) > 1 else 0,
            'volatility': float(df['returns'].std() * 100) if len(df) > 1 else 0,
            'sharpe_ratio': float(df['returns'].mean() / df['returns'].std() * np.sqrt(252)) if len(df) > 1 and df['returns'].std() > 0 else 0
        }
    }
    
    # Get prediction
    print(f"Training AI model for {symbol}...")
    prediction = train_and_predict_model(symbol)
    
    # Convert to JSON
    data_records = df.fillna(0).to_dict('records')
    for record in data_records:
        if isinstance(record['date'], pd.Timestamp):
            record['date'] = record['date'].strftime('%Y-%m-%d')
        for key, value in record.items():
            if isinstance(value, (np.integer, np.floating)):
                record[key] = float(value)
            elif pd.isna(value):
                record[key] = 0
    
    return jsonify({
        'symbol': symbol,
        'data': data_records,
        'statistics': stats_data,
        'prediction': prediction
    })

@app.route('/api/time-range/<symbol>', methods=['GET'])
def get_time_range_data(symbol):
    """Get data for specific time ranges"""
    range_type = request.args.get('range', '1Y')
    
    end_date = datetime.now()
    range_mapping = {
        '1D': timedelta(days=1),
        '1W': timedelta(weeks=1),
        '1M': timedelta(days=30),
        '3M': timedelta(days=90),
        '6M': timedelta(days=180),
        '1Y': timedelta(days=365),
        '5Y': timedelta(days=365*5),
        '10Y': timedelta(days=365*10),
        'ALL': timedelta(days=365*30)
    }
    
    start_date = end_date - range_mapping.get(range_type, timedelta(days=365))
    
    conn = get_db_connection()
    
    # Simple query for time range
    query = """
    SELECT symbol, date, close, low, high, volume
    FROM model_data 
    WHERE symbol = ? AND date BETWEEN ? AND ?
    ORDER BY date ASC
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        conn.close()
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    if df.empty:
        return jsonify({'error': 'No data found'}), 404
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Add open if not exists
    if 'open' not in df.columns:
        df['open'] = df['close']
    
    data_records = df.fillna(0).to_dict('records')
    for record in data_records:
        if isinstance(record['date'], pd.Timestamp):
            record['date'] = record['date'].strftime('%Y-%m-%d')
        for key, value in record.items():
            if isinstance(value, (np.integer, np.floating)):
                record[key] = float(value)
    
    return jsonify({
        'symbol': symbol,
        'range': range_type,
        'data': data_records,
        'total_records': len(data_records),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d'),
            'end': df['date'].max().strftime('%Y-%m-%d')
        }
    })

@app.route('/api/compare', methods=['POST'])
def compare_symbols():
    """Compare multiple symbols"""
    symbols = request.json.get('symbols', [])
    start_date = request.json.get('start_date', '1997-01-01')
    end_date = request.json.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    if not symbols or len(symbols) < 2:
        return jsonify({'error': 'At least 2 symbols required'}), 400
    
    conn = get_db_connection()
    comparison_data = {}
    
    for symbol in symbols:
        query = """
        SELECT date, close FROM model_data 
        WHERE symbol = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
        """
        df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['returns'] = df['close'].pct_change()
            df['normalized'] = (df['close'] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
            
            comparison_data[symbol] = {
                'dates': df['date'].dt.strftime('%Y-%m-%d').tolist(),
                'prices': df['close'].tolist(),
                'normalized': df['normalized'].fillna(0).tolist(),
                'returns': df['returns'].fillna(0).tolist()
            }
    
    conn.close()
    
    # Correlation matrix
    correlation_matrix = {}
    if len(comparison_data) >= 2:
        returns_df = pd.DataFrame({symbol: data['returns'] for symbol, data in comparison_data.items()})
        corr_matrix = returns_df.corr()
        correlation_matrix = {k: {k2: float(v2) for k2, v2 in v.items()} for k, v in corr_matrix.to_dict().items()}
    
    return jsonify({
        'comparison_data': comparison_data,
        'correlation_matrix': correlation_matrix
    })

if __name__ == '__main__':
    print("=" * 60)
    print("ForSight Analytics API Server")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Columns: {len(ACTUAL_COLUMNS)}")
    print("AI Models: Random Forest, Gradient Boosting, Linear Regression")
    print("=" * 60)
    app.run(debug=True, port=5000, host='0.0.0.0')
