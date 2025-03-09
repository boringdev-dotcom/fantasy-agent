# AI Chatbot - Perplexity.ai Inspired Interface

A modern AI chatbot interface inspired by Perplexity.ai, featuring a clean, minimal design with a focus on readability and user experience.

## Features

- **Clean, Minimal Design**: Inspired by Perplexity.ai's Scandinavian-like interface
- **Real-time WebSocket Communication**: Connect to any WebSocket backend
- **Source Citations**: Display sources for AI-generated responses
- **Responsive Layout**: Works on desktop and mobile devices
- **Modern UI Components**: Including avatars, message bubbles, and status indicators
- **Dark Mode Support**: Toggle between light and dark themes with automatic system preference detection

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- A running WebSocket server at ws://localhost:8765/ws/{sessionId}

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-chatbot.git
cd ai-chatbot
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm start
# or
yarn start
```

## WebSocket Connection

The application automatically connects to your WebSocket server at `ws://localhost:8765/ws/{sessionId}`, where `{sessionId}` is a randomly generated ID stored in localStorage. This allows the application to maintain a persistent connection across page reloads.

## WebSocket Message Format

The chatbot expects messages from your server in this JSON format:

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

You can customize the theme colors by modifying the theme definitions in `src/ThemeContext.tsx`:

```typescript
export const themes: Record<ThemeMode, ThemeColors> = {
  light: {
    background: '#f9fafb',
    text: '#1a1a1a',
    primary: '#2563eb',
    // ... other color definitions
  },
  dark: {
    background: '#111827',
    text: '#f3f4f6',
    primary: '#3b82f6',
    // ... other color definitions
  }
};
```

### Fonts

The app uses system fonts by default:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

## License

MIT

## Acknowledgements

- Design inspired by [Perplexity.ai](https://www.perplexity.ai/)
- Built with React and TypeScript
- Styled with styled-components