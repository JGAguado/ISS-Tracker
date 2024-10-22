from django.shortcuts import render
from django.http import JsonResponse
from .forms import UserLocationForm
from .models import ISSData
import numpy as np
import requests

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

    # Return the result as JSON
    return JsonResponse({
        'user_latitude': user_latitude,
        'user_longitude': user_longitude,
        'iss_latitude': iss_latitude,
        'iss_longitude': iss_longitude,
        'azimuth': azimuth,
        'elevation': elevation
    })

def track_iss(request):
    if request.method == 'POST':
        form = UserLocationForm(request.POST)
        if form.is_valid():
            user_lat = form.cleaned_data['latitude']
            user_long = form.cleaned_data['longitude']

            # Fetching ISS current position from Open Notify API
            # Attribution: This data is provided by Open Notify (http://open-notify.org)
            response = requests.get('http://api.open-notify.org/iss-now.json')
            iss_position = response.json()['iss_position']
            iss_lat = float(iss_position['latitude'])
            iss_long = float(iss_position['longitude'])

            azimuth, elevation = compute_azimuth_elevation(user_lat, user_long, iss_lat, iss_long)

            # Save the data
            iss_data = ISSData(
                user_latitude=user_lat,
                user_longitude=user_long,
                iss_latitude=iss_lat,
                iss_longitude=iss_long,
                azimuth=azimuth,
                elevation=elevation
            )
            iss_data.save()

            return render(request, 'tracking/results.html', {'iss_data': iss_data})
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