# Perplexity-Inspired AI Chatbot

## Overview

This project is a modern AI chatbot interface inspired by Perplexity.ai, featuring a clean, minimal design with a focus on readability and user experience. The interface connects to a WebSocket server to provide real-time responses to user queries.

## Key Features

1. **Clean, Minimal Design**: Inspired by Perplexity.ai's Scandinavian-like interface
2. **Real-time WebSocket Communication**: Connect to any WebSocket backend
3. **Source Citations**: Display sources for AI-generated responses
4. **Loading Animation**: Visual feedback while waiting for responses
5. **Responsive Layout**: Works on desktop and mobile devices
6. **Modern UI Components**: Including avatars, message bubbles, and status indicators
7. **Dark Mode Support**: Toggle between light and dark themes with automatic system preference detection

## Project Structure

- `src/App.tsx`: Main application component with UI and WebSocket logic
- `src/LoadingAnimation.tsx`: Loading animation component
- `src/index.tsx`: Entry point for the React application
- `src/ThemeContext.tsx`: Theme context provider for light/dark mode
- `src/ThemeToggle.tsx`: Theme toggle button component
- `start.js`: Script to run the client

## How to Run

1. Install dependencies:
   ```bash
   npm install
   ```

2. Make sure your WebSocket server is running at ws://localhost:8765/ws/{sessionId}

3. Start the client:
   ```bash
   npm start
   ```

   This will start:
   - React development server on http://localhost:3000

## WebSocket Connection

The application automatically connects to your WebSocket server at `ws://localhost:8765/ws/{sessionId}`, where `{sessionId}` is a randomly generated ID stored in localStorage. This allows the application to maintain a persistent connection across page reloads.

## Testing the Chatbot

Once the application is running, you can test it by:

1. Opening http://localhost:3000 in your browser
2. Typing a question in the search box and clicking "Ask"
3. The application will send your question to the WebSocket server
4. The server will respond with an answer and sources

Try these sample queries:
- "Hello"
- "What is AI?"
- "What are the latest AI trends?"
- "Tell me about Perplexity"

## Message Format

The chatbot expects messages from the server in this JSON format:

```json
{
  "text": "The response text",
  "sources": ["https://source1.com", "https://source2.com"]
}
```

When sending messages to the server, it uses:

```json
{
  "query": "User's question"
}
```

## Customization

### Theme

The application supports both light and dark themes. The theme is automatically detected based on the user's system preferences, but can be toggled using the theme toggle button in the header.

You can customize the theme colors by modifying the theme definitions in `src/ThemeContext.tsx`.

### Styling

The application uses styled-components for styling. You can customize the look and feel by modifying the styled components in `src/App.tsx`.

## Design Inspiration

The design is inspired by Perplexity.ai, featuring:

- Clean, minimal interface
- Focus on readability
- Source citations
- Loading animations
- Clear visual hierarchy
- Light and dark mode support

## Next Steps

To enhance this project further, consider:

1. Adding authentication
2. Implementing conversation history
3. Adding more advanced AI features like image generation
4. Creating a mobile app version
5. Adding internationalization support 