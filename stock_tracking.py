"""
Stock Tracking Module for Flask Application

This module provides functionality to track and display stock market data using the Polygon.io API.
It includes routes for viewing stock information, company details, and historical data.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify

# Create a Blueprint for stock tracking with URL prefix '/stocks'
stocks_bp = Blueprint('stocks', __name__, url_prefix='/stocks')

# API configuration
API_KEY = "EkQ7aRzKfOzxTOjBQ5yXVp1gw50G0ydH"  # Polygon.io API key
BASE_URL = "https://api.polygon.io"  # Base URL for Polygon API

# List of stock tickers to track
STOCKS = ["NVDA", "AAPL"]

def get_current_price(ticker):
    """
    Fetch the current price and market data for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        dict: Dictionary containing price data including:
            - ticker: Stock symbol
            - price: Current price
            - volume: Trading volume
            - change: Price change from open
            - change_percent: Percentage change from open
            - timestamp: Date of the data
        None: If the request fails or data is unavailable
    """
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
    """
    Fetch company information and details for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol
    
    Returns:
        dict: Dictionary containing company details including:
            - name: Company name
            - description: Business description
            - homepage_url: Company website
            - market_cap: Market capitalization
            - total_employees: Number of employees
        None: If the request fails or data is unavailable
    """
    endpoint = f"{BASE_URL}/v3/reference/tickers/{ticker}"
    params = {
        "apiKey": API_KEY
    }

    # Eployed the help of AI to make sure this was all correct and returned what I wanted
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

def get_historical_data(ticker, days=30):
    """
    Fetch historical price data for a stock ticker over a specified period.
    
    Args:
        ticker (str): The stock ticker symbol
        days (int): Number of days of historical data to retrieve (default: 30)
    
    Returns:
        list: List of dictionaries containing daily price data including:
            - date: Date of the data point
            - open: Opening price
            - high: Daily high price
            - low: Daily low price
            - close: Closing price
            - volume: Trading volume
        Empty list: If the request fails or data is unavailable
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    endpoint = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
    params = {
        "apiKey": API_KEY,
        "sort": "asc",
        "limit": 120
    }

    # I needed the help of AI to have the endpoint return what I wanted, though after reading the first few functions, it became pretty repetetive
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "OK":
            historical_data = []
            results = data.get("results", [])
            
            for result in results:
                historical_data.append({
                    "date": datetime.fromtimestamp(result.get("t") / 1000).strftime('%Y-%m-%d'),
                    "open": result.get("o"),
                    "high": result.get("h"),
                    "low": result.get("l"),
                    "close": result.get("c"),
                    "volume": result.get("v")
                })
            
            return historical_data
    except Exception as e:
        print(f"Error fetching historical data for {ticker}: {e}")
    
    return []

# Route Definitions

@stocks_bp.route('/')
def index():
    """
    Main stocks page showing overview of all tracked stocks.
    
    Returns:
        Rendered template 'stocks/index.html' with context containing:
            - stock_data: Dictionary mapping tickers to their price and company data
    """
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

@stocks_bp.route('/detail/<ticker>')
def detail(ticker):
    """
    Detailed view page for a specific stock.
    
    Args:
        ticker (str): The stock ticker symbol to display
    
    Returns:
        Rendered template 'stocks/detail.html' with context containing:
            - ticker: Stock symbol
            - price_data: Current price information
            - company_data: Company details
            - historical_data: Historical price data
        404 Error: If the ticker is not in the tracked stocks list
    """
    if ticker not in STOCKS:
        return "Stock not tracked", 404
    
    price_data = get_current_price(ticker)
    company_data = get_company_details(ticker)
    historical_data = get_historical_data(ticker)
    
    context = {
        "ticker": ticker,
        "price_data": price_data,
        "company_data": company_data,
        "historical_data": historical_data,
    }
    
    return render_template('stocks/detail.html', **context)

@stocks_bp.route('/api/data/<ticker>')
def api_data(ticker):
    """
    API endpoint to get JSON data for a specific stock.
    
    Args:
        ticker (str): The stock ticker symbol to retrieve data for
    
    Returns:
        JSON response containing:
            - ticker: Stock symbol
            - current: Current price data
            - historical: Historical price data
        404 Error: If the ticker is not in the tracked stocks list
    """
    if ticker not in STOCKS:
        return jsonify({"error": "Stock not tracked"}), 404
    
    price_data = get_current_price(ticker)
    historical_data = get_historical_data(ticker)

    # This was also assisted by AI to help understand how to not return an error with json in this instance
    return jsonify({
        "ticker": ticker,
        "current": price_data,
        "historical": historical_data
    })

def register_stocks_blueprint(app):
    """
    Register the stocks Blueprint with the Flask application and ensure template directory exists.
    
    Args:
        app (Flask): The Flask application instance
    """
    app.register_blueprint(stocks_bp)
    # Create a directory for the stock templates if it doesn't exist
    os.makedirs(os.path.join(app.template_folder, 'stocks'), exist_ok=True)
