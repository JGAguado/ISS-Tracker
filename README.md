
# ISS Tracker Django Application

The ISS Tracking and Speed Calculation System is a web-based application de-
signed to monitor the International Space Station’s (ISS) position and calculate
its speed based on GPS coordinates. The application allows users to enter their
geographic coordinates to receive real-time calculations for pointing their antenna
towards the ISS, including azimuth and elevation. Additionally, the system calcu-
lates the ISS’s average speed based on its last and current positions and displays
this data in the web interface.
The way to interact with the application is not only via a web interface for
the user to enter the coordinates, but also has a REST API endpoint that accepts
GET requests and returns the result in JSON format.

## Attribution

This project makes use of the Open Notify API for retrieving the current position of the International Space Station (ISS). You can learn more about Open Notify and their services at [Open Notify](http://open-notify.org).

Data provided by Open Notify:
- ISS Current Location: [http://api.open-notify.org/iss-now.json](http://api.open-notify.org/iss-now.json)

Special thanks to Open Notify for providing the ISS location data for free.

## Project Structure

### 1. Folders and files

- **`iss_tracker_app/`**: Contains the flask server that computes the ISS speed.
  - **`iss_tracker/`**: The main project folder containing the settings, URLs, and WSGI files.
      - **`settings.py`**: Contains configuration settings for the project such as installed apps, middleware, and database settings.
      - **`urls.py`**: Defines the routes for the project.
      - **`wsgi.py`**: Entry point for WSGI servers to serve the project.

  - **`tracking/`**: Contains the core logic for the tracking system.
      - **`models.py`**: Defines the `ISSData` model, which stores user and ISS coordinates along with the computed azimuth and elevation.
      - **`views.py`**: Contains the business logic to handle user input, make external API requests to Open Notify, compute azimuth and elevation, and render or return the data.
          - **`compute_azimuth_elevation`**: Computes the azimuth and elevation based on the geographical coordinates from the ISS, with respect to the user.
          - **`track_iss`**: Renders a form to receive user input and save into a Postgres DDBB the inquiry and the results.
          - **`track_iss_api`**: Provides a REST API endpoint to compute the azimuth and elevation based on user coordinates and ISS position.
      - **`forms.py`**: Defines the `UserLocationForm` that receives user input (latitude and longitude).
      - **`templates/`**: Contains the HTML files for rendering the form and result pages.

- **`iss_speed/`**: Contains the flask server that computes the ISS speed.
    - **`app.py`**: Receives the POST call, containing the previous and the current coordinates, correspondly timestampted and computes the average speed during that timeframe.


### 2. REST API

#### 2.1 Open-Notify API
This is the REST API that the ISS tracker application uses for retrieving the *live* data of the ISS with it's current position.

  - **Request Method**: `GET`
  - **Parameters**: None
  - **Response**: JSON response with the current ISS position.
  - **Example request**:
  ```
  curl -X GET "http://api.open-notify.org/iss-now"
  ```
  - **Example response (JSON format)**:
  ```
  {
    "user_latitude": "40.7128",
    "user_longitude": "-74.0060",
    "iss_latitude": 20.256,
    "iss_longitude": -30.456,
    "azimuth": 123.456,
    "elevation": 45.0
  }
  ```
#### 2.2 ISS Speed (Flask) API
This is the REST API that the ISS Speed flask server application offers to allow the computation of the ISS orbital speed out of input positions.
It's only used internally for allowing the interface between the ISS tracker main application (on django) and the flask server.

  - **Endpoint**: `/calculate-speed`
  - **Request Method**: `GET`
  - **Parameters**: `previous_latitude`, `previous_longitude`, `current_latitude`, `current_longitude`, `prev_timestamp`  (all are required)
  - **Response**: JSON response with the ISS speed.
  - **Example request**:
  ```
  curl -X GET "http://iss-speed:5000/calculate-speed?previous_latitude=40.7128&previous_longitude=-74.0060&current_latitude=34.0522&current_longitude=-118.2437&prev_timestamp=2024-10-24T16:21:20
"
  ```
  - **Example response (JSON format)**:
  ```
  {
    "speed": 25234.380999110348
  }
  ```
#### 2.3 ISS Tracker (Django) API
This is the REST API offered by the main application to provide the same output data out of the same input data as the web application.

  - **Endpoint**: `/api/track_iss/`
  - **Request Method**: `GET`
  - **Parameters**: `latitude`, `longitude` (both required)
  - **Response**: JSON response with the user's coordinates, ISS position and speed, computed azimuth, and elevation.
  - **Example request**:
  ```
  curl -X GET "http://localhost:8000/api/track_iss/?latitude=56.1612&longitude=-15.5869"
  ```
  - **Example response (JSON format)**:
  ```
    {
    "user_latitude": "56.1612", 
    "user_longitude": "-15.5869", 
    "iss_latitude": -33.3092, 
    "iss_longitude": 163.7244, 
    "iss_speed": 24773.385563774205, 
    "azimuth": 1.4818818929146573, 
    "elevation": -67.1430405092625
    }
  ```

### 3. Dockerfiles

Two different dockerfiles are provided for the individual testing of the django and flask services.

- **ISS tracker (Django)**: The \`Dockerfile\` is used to containerize the Django application, ensuring it can be deployed in any environment.
The docker image can be found in Docker-hub ([jongaguado/iss-tracker:latest](https://hub.docker.com/r/jongaguado/iss-tracker)). 

- **ISS speed (Flask)**: The \`Dockerfile\` is used to containerize the Flask application, ensuring it can be deployed in any environment.
The docker image can be found in Docker-hub ([jongaguado/flask-iss-speed:latest](https://hub.docker.com/r/jongaguado/flask-iss-speed)).

#### 3.1 Docker compose
Additionally, and as a way to run both containers in a way that they can easily interact with each other, a docker compose file is presented as well.
The images of each of the containers are pulled from Docker-hub, but they could be easily built up from each local dockerfiles.

### 4. Kubernetes Configuration

The application is containerized using Docker and can be deployed to a Kubernetes cluster. Kubernetes manifests are created to ensure each microservice (Django app, Flask app and the PostgreSQL database) is horizontally scalable and exposed properly to the outside.

The YAML files containing the Kubernetes deployment setup are contained inside of the following folder found in the repository root.


- **`kubernetes/`**: 
  - **\`secrets.yaml\`**: Stores sensitive credentials such as the PostgreSQL password securely.
  - **\`postgres-deployment.yaml\`**: Defines the PostgreSQL database deployment and persistent volume claim as well as the service.
  - **\`django-deployment.yaml\`**: Defines the deployment for the Django app, with environment variables linked to the database, and the services.
  - **\`flask-deployment.yaml\`**: Defines the deployment for the Flask app and the service.

---

## Instructions to Run the Application

### 1. Local Setup

If you want to run the application locally, follow these steps:

#### Prerequisites

- Python 3.10+
- PostgreSQL

#### Clone the repository:

```
git clone https://github.com/JGAguado/ISS-Tracker.git
cd iss_tracker
```

#### Install Python Dependencies:

```
pip install -r requirements.txt
```

Make sure that the url address(views.py file) for the ISS speed calculation is the localhosted and not 
the *container* app.

```
url = 'http://127.0.0.1:5000/calculate-speed'
# url = 'http://iss-speed:5000/calculate-speed'
```

#### Set Up PostgreSQL

Make sure to set up PostgreSQL either locally or in a container.

- Create a database \`iss_db\`.
- Create a user \`iss_user\` with a password.
- Grant necessary permissions to the user.

When testing this method, make sure to uncomment the *Django localhost* DATABASES dictionary on the iss_tracker\settings.py 
and comment the *Docker* DATABASES dictionary. 

#### Migrate the Database:

```
python manage.py migrate
```

#### Run the Server Locally:

```
python manage.py runserver
```

Access the app at \`http://localhost:8000\`.

### 2. Docker Setup

The easiest and simplest option is to run the docker-compose.yaml file that will provide all the necessary files, 
pulled from Docker-hub, and leave the app ready to run:

```
docker-compose up
```

Alternatively, each of the containers from the previous steps could be built up

```
docker build -t iss-tracker .
cd flask_app
docker build -t iss-speed .
```

Or even be pulled from Docker Hub

```
docker pull jongaguado/iss-tracker:latest
docker pull jongaguado/iss-speed:latest
```

In this case you will need to apply migrations in Docker manually:

```
docker-compose exec web python manage.py migrate
```

And then run the Docker containers:

```
docker run -d -p 8000:8000 jongaguado/iss-tracker
docker run -d -p 5000:5000 jongaguado/iss-speed
```

### 3. Kubernetes Deployment

To deploy the application to Kubernetes:

#### Prerequisites:

- Install Kubernetes CLI (\`kubectl\`) or enable Kubernetes in the Docker Desktop application.
- Ensure Docker Hub access for pulling images.

#### Step-by-Step Deployment:

1. **Secrets for Database Credentials:**

Edit the pulled **`kubernetes\secrets.yaml\`** with your own database name, user and password.

> :warning: **Important**: The content of the key "data" hast to be encoded in Base64. This **is an encoding, not an encription**,
> but it ensures data format compatibility with the YAML files, provides a minimal form of obfuscation, and handles binary or special characters securely

And then create it

```
kubectl apply -f secrets.yaml
```

2. **Deploy PostgreSQL Database, PV & PVC, and it's service:**

```
kubectl apply -f database-deployment.yaml
```

3. **Deploy Django Application and it's service:**

```
kubectl apply -f iss-tracker.yaml
```

4. **Deploy Flask Application and it's service:**

```
kubectl apply -f iss-speed.yaml
```


#### Verifying Deployment

- Use \`kubectl get pods\` to ensure all pods are running.

