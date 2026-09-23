from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track_shipment():
    data = request.get_json()
    courier = data.get('courier').upper()
    tracking_no = data.get('tracking_number')
    
    if not tracking_no:
        return jsonify({'success': False, 'message': 'Please enter a tracking number'})

    url = ""
    if courier == 'DTDC':
        url = f"https://www.dtdc.in/tracking/shipment-tracking.asp?strCnno={tracking_no}"
    elif courier == 'PROFESSIONAL':
        url = f"https://www.theprofessionalcouriers.com/track?billNo={tracking_no}"
    elif courier == 'TRACKON':
        url = f"https://trackon.in/track?trackingNo={tracking_no}"
    elif courier == 'DELHIVERY':
        url = f"https://www.delhivery.com/track/package/{tracking_no}"
    elif courier == 'SUPERFAST':
        url = f"https://www.superfastcourier.com/tracking?waybill={tracking_no}"
    elif courier == 'DHL':
        url = f"https://www.dhl.com/en/express/tracking.html?AWB={tracking_no}"
    else:
        return jsonify({'success': False, 'message': 'Selected courier not supported yet'})
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Connected successfully message (you can write specific tags parser later for each)
        return jsonify({
            'success': True, 
            'status': f'Connected to {courier} successfully. Tracking ID: {tracking_no}'
        })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Scraping error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

