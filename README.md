
# ISS Tracker Django Application

This Django application allows users to enter their geographical coordinates (latitude and longitude) to compute the azimuth and elevation required to point an antenna towards the International Space Station (ISS). The application uses a REST API to retrieve the current position of the ISS and calculates the azimuth and elevation based on the user's location.

This educational example not only presents a web interface for the user to enter the coordinates, but also has a REST API endpoint that accepts GET requests and returns the result in JSON format.

## Attribution

This project makes use of the Open Notify API for retrieving the current position of the International Space Station (ISS). You can learn more about Open Notify and their services at [Open Notify](http://open-notify.org).

Data provided by Open Notify:
- ISS Current Location: [http://api.open-notify.org/iss-now.json](http://api.open-notify.org/iss-now.json)

Special thanks to Open Notify for providing the ISS location data for free.

## Project Structure

### 1. Django App Structure

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


### 2. REST API

- **Endpoint**: `/api/track_iss/`
- **Request Method**: `GET`
- **Parameters**: `latitude`, `longitude` (both required)
- **Response**: JSON response with the user's coordinates, ISS position, computed azimuth, and elevation.

Example request:
```
curl -X GET "http://localhost:8000/api/track_iss/?latitude=40.7128&longitude=-74.0060"
```

Example response (JSON format):
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

### 3. Dockerfile

The \`Dockerfile\` is used to containerize the Django application, ensuring it can be deployed in any environment.

- **Base Image**: \`python:3.10-slim\`
- **Commands**:
    - Install system dependencies (\`build-essential\`, \`libpq-dev\`).
    - Install required Python libraries (\`requirements.txt\`).
    - Set environment variables for Django.
    - Expose port 8000.

### 4. Kubernetes Configuration

The application is containerized using Docker and can be deployed to a Kubernetes cluster. Kubernetes manifests are created to ensure each microservice (Django app, PostgreSQL database) is horizontally scalable and exposed properly to the outside.

The YAML files containing the Kubernetes deployment setup are contained inside of the following folder found in the repository root.


- **`kubernetes/`**: 
  - **\`secrets.yaml\`**: Stores sensitive credentials such as the PostgreSQL password securely.
  - **\`postgres-deployment.yaml\`**: Defines the PostgreSQL database deployment and persistent volume claim.
  - **\`django-deployment.yaml\`**: Defines the deployment for the Django app, with environment variables linked to the database.
  - **\`services.yaml\`**: Exposes both the database and Django app as services.

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

#### Set Up PostgreSQL

Make sure to set up PostgreSQL either locally or in a container.

- Create a database \`iss_db\`.
- Create a user \`iss_user\` with a password.
- Grant necessary permissions to the user.

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

To run the app in Docker:

1. Option A: Build the Docker image

If you followed the previous steps, you can build it out of the \`Dockerfile\`:

```
docker build -t jongaguado/iss-tracker .
```

2. Option B: Pull it from Docker Hub

```
docker pull jongaguado/iss-tracker:latest
```

In this case you will need to apply migrations in Docker:

```
docker-compose exec web python manage.py migrate
```

This will run the migrations inside the Docker container and set up the PostgreSQL database.
3. Run the Docker container:

```
docker run -d -p 8000:8000 jongaguado/iss-tracker
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

2. **Deploy PostgreSQL Database:**

```
kubectl apply -f postgres-deployment.yaml
```

3. **Deploy Django Application:**

```
kubectl apply -f django-deployment.yaml
```

4. **Expose Services:**

```
kubectl apply -f services.yaml
```


#### Verifying Deployment

- Use \`kubectl get pods\` to ensure all pods are running.
- Use \`kubectl get services\` to check the external IP address or domain where the app is accessible.

###