"""
app.py  —  Tamil Calendar Flask server
Run:  python app.py
Open: http://localhost:5050
"""

import datetime
from flask import Flask, request, jsonify, send_from_directory
from tamil_calendar import (
    build_tamil_calendar,
    get_today_tamil_date,
    DEFAULT_LAT, DEFAULT_LON,
    MONTH_ENGLISH,
)

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/calendar')
def api_calendar():
    try:
        year  = int(request.args.get('year',  datetime.date.today().year))
        month = int(request.args.get('month', datetime.date.today().month))
        lat   = float(request.args.get('lat', DEFAULT_LAT))
        lon   = float(request.args.get('lon', DEFAULT_LON))
        ayan  = request.args.get('ayan', 'lahiri')

        days = build_tamil_calendar(year, month, lat, lon, ayan)
        return jsonify({
            'year':       year,
            'month':      month,
            'month_name': MONTH_ENGLISH[month - 1],
            'days':       days,
            'total_days': len(days),
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/today')
def api_today():
    try:
        lat  = float(request.args.get('lat', DEFAULT_LAT))
        lon  = float(request.args.get('lon', DEFAULT_LON))
        ayan = request.args.get('ayan', 'lahiri')
        data = get_today_tamil_date(lat, lon, ayan)
        return jsonify(data or {'error': 'not found'})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Tamil Calendar server starting on http://localhost:5050")
    app.run(debug=True, port=5050)
