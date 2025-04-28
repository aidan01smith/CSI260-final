import os
import requests
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify

# Create a Blueprint for stock tracking
stocks_bp = Blueprint('stocks', __name__, url_prefix='/stocks')

# Polygon.io API key
API_KEY = "EkQ7aRzKfOzxTOjBQ5yXVp1gw50G0ydH"
BASE_URL = "https://api.polygon.io"

# Define the stocks to track
STOCKS = ["NVDA", "AAPL"]

def get_current_price(ticker):
    endpoint = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev"
    params = {
        "apiKey": API_KEY
    }
    
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "OK":
            results = data.get("results", [])
            if results:
                return {
                    "ticker": ticker,
                    "price": results[0].get("c"),
                    "volume": results[0].get("v"),
                    "change": results[0].get("c") - results[0].get("o"),
                    "change_percent": ((results[0].get("c") - results[0].get("o")) / results[0].get("o")) * 100,
                    "timestamp": datetime.fromtimestamp(results[0].get("t") / 1000).strftime('%Y-%m-%d')
                }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
    
    return None

def get_company_details(ticker):
    endpoint = f"{BASE_URL}/v3/reference/tickers/{ticker}"
    params = {
        "apiKey": API_KEY
    }
    
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "OK":
            result = data.get("results", {})
            return {
                "name": result.get("name"),
                "description": result.get("description"),
                "homepage_url": result.get("homepage_url"),
                "market_cap": result.get("market_cap"),
                "total_employees": result.get("total_employees")
            }
    except Exception as e:
        print(f"Error fetching company details for {ticker}: {e}")
    
    return None


# Create routes for the stock tracking functionality
@stocks_bp.route('/')
def index():
    """Main stocks page showing overview of tracked stocks"""
    stock_data = {}
    
    for ticker in STOCKS:
        price_data = get_current_price(ticker)
        company_data = get_company_details(ticker)
        
        if price_data and company_data:
            stock_data[ticker] = {
                "price_data": price_data,
                "company_data": company_data
            }
    
    return render_template('stocks/index.html', stock_data=stock_data)

@stocks_bp.route('/api/data/<ticker>')
def api_data(ticker):
    """API endpoint to get stock data"""
    if ticker not in STOCKS:
        return jsonify({"error": "Stock not tracked"}), 404
    
    price_data = get_current_price(ticker)
    historical_data = get_historical_data(ticker)
    
    return jsonify({
        "ticker": ticker,
        "current": price_data,
        "historical": historical_data
    })

# Function to register the Blueprint with the Flask app
def register_stocks_blueprint(app):
    app.register_blueprint(stocks_bp)
    # Create a directory for the stock templates if it doesn't exist
    os.makedirs(os.path.join(app.template_folder, 'stocks'), exist_ok=True)
