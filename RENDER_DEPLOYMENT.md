# Deploying Fantasy Agent to Render

This guide explains how to deploy the Fantasy Agent application to Render.

## Prerequisites

- A [Render](https://render.com) account
- Your code pushed to a GitHub repository

## Deployment Steps

### Option 1: Using the Blueprint (Recommended)

1. Log in to your Render account
2. Click on the "New" button and select "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file and set up the services
5. Click "Apply" to start the deployment

### Option 2: Manual Deployment

If you prefer to set up the services manually:

#### Backend Deployment

1. Log in to your Render account
2. Click on the "New" button and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Name: `fantasy-agent-backend`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd agent && python server.py`
   - Environment Variables:
     - `PYTHON_VERSION`: `3.9.0`
5. Click "Create Web Service"

#### Frontend Deployment

1. Click on the "New" button and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - Name: `fantasy-agent-frontend`
   - Environment: `Node`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve -s build`
   - Environment Variables:
     - `NODE_VERSION`: `18.x`
     - `REACT_APP_API_URL`: URL of your backend service (e.g., `https://fantasy-agent-backend.onrender.com`)
4. Click "Create Web Service"

## Verifying Deployment

1. Once both services are deployed, navigate to your frontend URL
2. The application should connect to the backend WebSocket automatically
3. Test the functionality to ensure everything is working correctly

## Troubleshooting

- Check the logs in the Render dashboard for any errors
- Ensure all environment variables are set correctly
- Verify that the WebSocket connection is working by checking the browser console 