from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .forms import UserLocationForm
from .models import ISSData
import numpy as np
import requests
from datetime import timedelta

def compute_azimuth_elevation(user_lat, user_long, iss_lat, iss_long):
    # Calculation logic for azimuth and elevation
    delta_long = np.radians(iss_long - user_long)
    user_lat_rad = np.radians(user_lat)
    iss_lat_rad = np.radians(iss_lat)

    # Compute azimuth
    x = np.sin(delta_long) * np.cos(iss_lat_rad)
    y = np.cos(user_lat_rad) * np.sin(iss_lat_rad) - np.sin(user_lat_rad) * np.cos(iss_lat_rad) * np.cos(delta_long)
    azimuth = (np.degrees(np.arctan2(x, y)) + 360) % 360

    # Compute elevation
    elevation = np.degrees(np.arcsin(np.sin(user_lat_rad) * np.sin(iss_lat_rad) + np.cos(user_lat_rad) * np.cos(iss_lat_rad) * np.cos(delta_long)))

    return azimuth, elevation

def track_iss_api(request):
    user_latitude = request.GET.get('latitude')
    user_longitude = request.GET.get('longitude')

    if user_latitude is None or user_longitude is None:
        return JsonResponse({'error': 'Missing latitude or longitude parameters'}, status=400)

    # Fetching ISS current position from Open Notify API
    # Attribution: This data is provided by Open Notify (http://open-notify.org)
    response = requests.get("http://api.open-notify.org/iss-now.json")
    if response.status_code != 200:
        return JsonResponse({'error': 'Could not retrieve ISS position'}, status=500)

    iss_position = response.json()
    iss_latitude = float(iss_position['iss_position']['latitude'])
    iss_longitude = float(iss_position['iss_position']['longitude'])

    # Compute azimuth and elevation
    azimuth, elevation = compute_azimuth_elevation(float(user_latitude), float(user_longitude), iss_latitude, iss_longitude)

    # Save the data
    iss_data = ISSData(
        user_latitude=user_latitude,
        user_longitude=user_longitude,
        iss_latitude=iss_latitude,
        iss_longitude=iss_longitude,
        iss_speed=0,
        azimuth=azimuth,
        elevation=elevation
    )
    iss_data.save()

    # Return the result as JSON
    return JsonResponse({
        'user_latitude': user_latitude,
        'user_longitude': user_longitude,
        'iss_latitude': iss_latitude,
        'iss_longitude': iss_longitude,
        'iss_speed':0,
        'azimuth': azimuth,
        'elevation': elevation
    })

def track_iss(request):
    if request.method == 'POST':
        form = UserLocationForm(request.POST)
        if form.is_valid():
            user_latitude = form.cleaned_data['latitude']
            user_longitude = form.cleaned_data['longitude']



            # Fetching ISS current position from Open Notify API
            # Attribution: This data is provided by Open Notify (http://open-notify.org)
            response = requests.get('http://api.open-notify.org/iss-now.json')
            iss_position = response.json()['iss_position']
            iss_latitude = float(iss_position['latitude'])
            iss_longitude = float(iss_position['longitude'])

            azimuth, elevation = compute_azimuth_elevation(user_latitude, user_longitude, iss_latitude, iss_longitude)

            # Get the last stored ISS data from the database to compute speeds
            last_data = ISSData.objects.last()

            if last_data:
                # Get the time difference between the last sample and the current time
                time_diff = timezone.now() - last_data.timestamp

                # If time difference exceeds 1 hour, return an error
                # if time_diff > timedelta(hours=1):
                    # return JsonResponse({
                    #     'error': 'The time difference between the last sample and the current time is too large (more than 1 hour). Speed calculation not possible.'
                    # })

                # Call Flask microservice to calculate speed
                # url = 'http://127.0.0.1:5000/calculate-speed'
                url = 'http://flask:5000/calculate-speed'

                data = {
                    "previous_latitude": last_data.iss_latitude,
                    "previous_longitude": last_data.iss_longitude,
                    "current_latitude": iss_latitude,
                    "current_longitude": iss_longitude,
                    "prev_timestamp": last_data.timestamp.isoformat()  # Use your ISO formatted timestamp
                }

                response = requests.post(url, json=data)
                speed_data = response.json()
            else:
                speed_data = {'speed': None, 'message': 'No previous data available to calculate speed.'}

            # Save the data
            iss_data = ISSData(
                user_latitude=user_latitude,
                user_longitude=user_longitude,
                iss_latitude=iss_latitude,
                iss_longitude=iss_longitude,
                iss_speed=speed_data.get('speed', None),
                azimuth=azimuth,
                elevation=elevation
            )
            iss_data.save()

            return render(request, 'tracking/results.html', {
                'iss_data': iss_data
            })
    else:
        form = UserLocationForm()

    return render(request, 'tracking/form.html', {'form': form})


def iss_form_view(request):
    if request.method == 'POST':
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']

        # Dummy data for now, you would calculate the ISS position and other results here
        iss_latitude = 51.0  # Replace this with real API data
        iss_longitude = -0.1  # Replace this with real API data
        azimuth = 120.5  # Replace this with calculated value
        elevation = 45.0  # Replace this with calculated value

        context = {
            'user_latitude': latitude,
            'user_longitude': longitude,
            'iss_latitude': iss_latitude,
            'iss_longitude': iss_longitude,
            'azimuth': azimuth,
            'elevation': elevation,
        }

        return render(request, 'tracking/results.html', context)

    return render(request, 'tracking/form.html')