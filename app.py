from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

def load_assets():
    with open('assets.json', 'r') as f:
        return json.load(f)

def calculate_compound_interest(principal, years, annual_rate, compounding_freq):
    """Calculate compound interest"""
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
    return render_template('index.html')

@app.route('/api/assets')
def get_assets():
    assets = load_assets()
    return jsonify(assets)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        principal = float(data.get('principal', 100000))
        years = int(data.get('years', 5))
        
        assets = load_assets()
        results = []
        
        for asset in assets:
            # Determine compounding frequency
            asset_type = asset['type']
            if asset_type in ['sacco', 'bank_interest', 'mmf']:
                compounding = 'monthly'
            elif asset_type == 'treasury_bills':
                compounding = 'quarterly'
            else:
                compounding = 'annually'
            
            final_amount = calculate_compound_interest(
                principal, 
                years, 
                asset['rate'], 
                compounding
            )
            
            returns = final_amount - principal
            roi = (returns / principal) * 100
            
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
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)