from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime

app = Flask(__name__)

def load_assets():
    """Load assets data from JSON file"""
    try:
        with open('assets.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default assets if file doesn't exist
        return get_default_assets()

def get_default_assets():
    """Return default asset data"""
    return [
        {
            "name": "SACCO Dividends",
            "type": "sacco",
            "rate": 12.5,
            "risk": "Medium",
            "liquidity": "Medium",
            "min_investment": 1000,
            "description": "Cooperative society dividends with annual payout, typically offering higher returns than banks"
        },
        {
            "name": "Money Market Fund",
            "type": "mmf",
            "rate": 9.8,
            "risk": "Low",
            "liquidity": "High",
            "min_investment": 500,
            "description": "Low-risk mutual funds investing in short-term securities with daily liquidity"
        },
        {
            "name": "Bank Fixed Deposit",
            "type": "bank_interest",
            "rate": 7.5,
            "risk": "Low",
            "liquidity": "Low",
            "min_investment": 5000,
            "description": "Fixed-term bank deposits offering guaranteed returns with low risk"
        },
        {
            "name": "91-Day Treasury Bill",
            "type": "treasury_bills",
            "rate": 16.2,
            "risk": "Low",
            "liquidity": "Medium",
            "min_investment": 100000,
            "description": "Government short-term securities offering competitive risk-free returns"
        },
        {
            "name": "Infrastructure Bond",
            "type": "bonds",
            "rate": 14.5,
            "risk": "Low",
            "liquidity": "Low",
            "min_investment": 100000,
            "description": "Government infrastructure bonds with semi-annual interest payments"
        },
        {
            "name": "Rental Property (Nairobi)",
            "type": "rental",
            "rate": 8.0,
            "risk": "Medium",
            "liquidity": "Low",
            "min_investment": 3000000,
            "description": "Residential property investment with rental income and potential capital appreciation"
        },
        {
            "name": "Land Appreciation",
            "type": "land",
            "rate": 15.0,
            "risk": "Medium",
            "liquidity": "Low",
            "min_investment": 500000,
            "description": "Land purchase in developing areas with potential for significant value appreciation"
        }
    ]

def calculate_compound_interest(principal, years, annual_rate, compounding_freq):
    """Calculate compound interest with different compounding frequencies"""
    if compounding_freq == 'annually':
        n = 1
    elif compounding_freq == 'quarterly':
        n = 4
    elif compounding_freq == 'monthly':
        n = 12
    else:
        n = 1
    
    rate = annual_rate / 100
    amount = principal * (1 + rate/n) ** (n * years)
    return round(amount, 2)

@app.route('/')
def home():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/assets')
def get_assets():
    """API endpoint to get all investment assets"""
    assets = load_assets()
    return jsonify(assets)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint to calculate investment returns"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        principal = float(data.get('principal', 100000))
        years = int(data.get('years', 5))
        
        # Validate inputs
        if principal < 1000:
            return jsonify({'error': 'Minimum investment is KES 1,000'}), 400
        if years < 1 or years > 30:
            return jsonify({'error': 'Investment period must be between 1 and 30 years'}), 400
        
        assets = load_assets()
        results = []
        
        for asset in assets:
            # Determine compounding frequency based on asset type
            asset_type = asset['type']
            if asset_type in ['sacco', 'bank_interest', 'mmf']:
                compounding = 'monthly'
            elif asset_type == 'treasury_bills':
                compounding = 'quarterly'
            else:
                compounding = 'annually'
            
            # Calculate final amount
            final_amount = calculate_compound_interest(
                principal, 
                years, 
                asset['rate'], 
                compounding
            )
            
            # Calculate returns and ROI
            returns = final_amount - principal
            roi = (returns / principal) * 100 if principal > 0 else 0
            
            results.append({
                'name': asset['name'],
                'rate': asset['rate'],
                'final_amount': final_amount,
                'returns': round(returns, 2),
                'roi': round(roi, 2),
                'risk': asset['risk'],
                'liquidity': asset['liquidity']
            })
        
        return jsonify(results)
        
    except ValueError as e:
        return jsonify({'error': 'Invalid input values'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT
    print("Starting Kenya Investment Comparator...")
    print(f"Server running at: http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)