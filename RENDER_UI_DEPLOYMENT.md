# Deploying the Fantasy Agent UI to Render

This guide explains how to deploy the Fantasy Agent UI to Render.com, connecting to the websocket backend at `wss://fantasy-agent.onrender.com/ws/{session_id}`.

## Prerequisites

- A Render.com account
- Git repository with the Fantasy Agent UI code

## Deployment Steps

1. Log in to your Render.com account
2. Click on "New" and select "Web Service"
3. Connect your Git repository
4. Configure the service with the following settings:
   - **Name**: fantasy-agent-frontend (or your preferred name)
   - **Environment**: Node
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx serve -s build`
   - **Environment Variables**:
     - `NODE_VERSION`: 18.x
     - `REACT_APP_WEBSOCKET_URL`: wss://fantasy-agent.onrender.com/ws

5. Click "Create Web Service"

## Verification

After deployment is complete:

1. Visit your deployed UI at the URL provided by Render
2. Open the browser console (F12) to verify the WebSocket connection
3. Test the UI by sending a message and confirming it connects to the backend

## Troubleshooting

- If the WebSocket connection fails, check that the `REACT_APP_WEBSOCKET_URL` environment variable is correctly set
- Ensure your backend service at `wss://fantasy-agent.onrender.com/ws` is running and accessible
- Check the browser console for any error messages related to WebSocket connections

## Alternative Deployment Method

You can also use the `render.yaml` file included in this repository for deployment:

1. Fork this repository
2. Connect your Render account to your GitHub account
3. Create a new "Blueprint" deployment in Render, pointing to your forked repository
4. Render will automatically detect the `render.yaml` file and set up the service accordingly 