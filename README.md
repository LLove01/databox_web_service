# Service Deployment

This repository contains a service that extracts metrics from different data sources and sends them to the Databox platform via Push API. Below are the deployment instructions for deploying the service using Docker or manually.

## Docker Deployment

### Prerequisites
- Docker installed on your machine

### Steps
1. Clone this repository to your local machine.  
2. Navigate to the root directory of the project.
3. Open a terminal or command prompt.
4. Run the following command to build the Docker images and start the containers:

>*docker-compose up --build*

or for detached mode:

>*docker-compose up --build -d*


5. Wait for the build process to complete. Once finished, you should see the backend and frontend services running.
6. Access the frontend of the application by opening a web browser and visiting http://localhost:3000.
7. To stop the containers, press Ctrl + C in the terminal where Docker Compose is running.

## Manual Deployment

### Prerequisites
Python 3.x installed on your machine
Node.js and npm installed on your machine

### Backend setup 

1. Clone this repository to your local machine.
2. Navigate to the backend directory.
3. Create a virtual environment by running:

 > *python -m venv venv*

4. Activate the virtual environment:

  windows: venv\Scripts\activate
  macOS/Linux: source venv/bin/activate

5. Install the Python dependencies:
   
> *pip install -r requirements.txt*

6. Run the FastAPI server:
   
> cwd must be root directory, not backend
> *uvicorn backend.main:app --reload*

### Frontend setup

1. Open a new terminal window/tab.
2. Navigate to the frontend directory.
3. Install the required npm packages:

 > *npm install*

4. Start React development server:

> *npm start*

5. Access the frontend of the application by opening a web browser and visiting http://localhost:3000.

### Note

Make sure to configure the necessary environment variables, such as GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET, before running the service.

## Databox Dashboard

A Databox dashboard has been prepared to display the metrics pushed by the service. 
You can access the dashboard via the following link:

https://app.databox.com/datawall/ac5a85a22e739907f59fc9e70c155cda567265465c7b922
