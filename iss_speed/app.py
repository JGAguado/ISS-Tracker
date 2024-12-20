from flask import Flask, request, jsonify
import math
from datetime import datetime, timezone

app = Flask(__name__)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers

@app.route('/calculate-speed', methods=['GET'])
def calculate_speed():
    # Extracting query parameters from the URL
    try:
        prev_lat = float(request.args.get('previous_latitude'))
        prev_lon = float(request.args.get('previous_longitude'))
        curr_lat = float(request.args.get('current_latitude'))
        curr_lon = float(request.args.get('current_longitude'))
        prev_timestamp = datetime.fromisoformat(request.args.get('prev_timestamp'))
    except (TypeError, ValueError) as e:
        return jsonify({'error': 'Invalid or missing parameter(s)'}), 400


    # Parse the timestamps
    # prev_timestamp = datetime.fromisoformat(data['prev_timestamp'])
    current_timestamp = datetime.now(timezone.utc)  # Use server time to match Django's timezone.now()

    # Calculate time difference in seconds
    time_difference = (current_timestamp - prev_timestamp).total_seconds()

    distance = haversine(prev_lat, prev_lon, curr_lat, curr_lon)
    # Speed in km/h = distance (km) / time (hours)
    if time_difference > 0:
        speed = distance / (time_difference / 3600)  # Convert seconds to hours
    else:
        return jsonify({'error': 'Invalid time difference'})

    return jsonify({'speed': speed})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
