from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)
CORS(app)

def scrape_courier_status(courier, tracking_no):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            if courier == 'dtdc':
                page.goto("https://www.dtdc.in/tracking.asp", timeout=25000)
                page.fill('#strcnno', tracking_no)
                page.click('#btnSubmit')
                page.wait_for_selector('.tracking-result-box', timeout=10000)
                status = page.inner_text('.status-text')
                browser.close()
                return {'success': True, 'courier': 'DTDC', 'tracking_no': tracking_no, 'booking_date': 'Available on Site', 'expected_delivery': 'In Transit', 'status': status}

            elif courier == 'delhivery':
                page.goto(f"https://www.delhivery.com/track/package/{tracking_no}", timeout=25000)
                page.wait_for_selector('.tracking-status', timeout=10000)
                status = page.inner_text('.tracking-status')
                browser.close()
                return {'success': True, 'courier': 'Delhivery', 'tracking_no': tracking_no, 'booking_date': 'N/A', 'expected_delivery': 'In Transit', 'status': status}

            browser.close()
            return {'success': False, 'message': 'Selected courier service scraping failed or unsupported.'}

        except Exception as e:
            browser.close()
            return {'success': False, 'message': f'Tracking failed. Details not found or invalid number.'}

@app.route('/track', methods=['POST'])
def track():
    data = request.json or {}
    courier = data.get('courier')
    tracking_no = data.get('tracking_no')

    if not courier or not tracking_no:
        return jsonify({'success': False, 'message': 'Courier and Tracking Number required'}), 400

    res = scrape_courier_status(courier, tracking_no)
    return jsonify(res)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
