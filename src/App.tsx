import React, { useState, useEffect, useCallback, useRef } from 'react';
import styled, { css } from 'styled-components';
import LoadingAnimation from './LoadingAnimation';
import ThemeToggle from './ThemeToggle';
import { useTheme } from './ThemeContext';

// Styled components with Perplexity-inspired design
const AppContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${props => props.theme.background};
  color: ${props => props.theme.text};
  transition: background-color 0.3s ease, color 0.3s ease;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  border-bottom: 1px solid ${props => props.theme.border};
  padding-bottom: 15px;
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: 600;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const LogoIcon = styled.div`
  width: 28px;
  height: 28px;
  position: relative;
  
  &::before, &::after {
    content: '';
    position: absolute;
    background-color: ${props => props.theme.primary};
  }
  
  &::before {
    width: 100%;
    height: 2px;
    top: 50%;
    left: 0;
    transform: translateY(-50%);
  }
  
  &::after {
    width: 2px;
    height: 100%;
    left: 50%;
    top: 0;
    transform: translateX(-50%);
  }
`;

const NavLinks = styled.div`
  display: flex;
  gap: 20px;
  align-items: center;
`;

const NavLink = styled.a`
  color: ${props => props.theme.secondary};
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  
  &:hover {
    color: ${props => props.theme.primary};
  }
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const SearchContainer = styled.div`
  position: relative;
  margin-bottom: 30px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 15px 20px;
  font-size: 16px;
  border: 2px solid ${props => props.theme.border};
  border-radius: 12px;
  outline: none;
  transition: border-color 0.2s;
  background-color: ${props => props.theme.inputBackground};
  color: ${props => props.theme.text};

  &:focus {
    border-color: ${props => props.theme.primary};
  }
`;

const SearchButton = styled.button`
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background-color: ${props => props.theme.primary};
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${props => props.theme.primary}dd;
  }

  &:disabled {
    background-color: ${props => props.theme.border};
    cursor: not-allowed;
  }
`;

const MessageContainer = styled.div`
  margin-top: 20px;
  padding: 15px;
  background-color: ${props => props.theme.cardBackground};
  border-radius: 12px;
  max-height: 60vh;
  overflow-y: auto;
  flex: 1;
  transition: background-color 0.3s ease;
`;

const Message = styled.div<{ isUser: boolean }>`
  margin: 16px 0;
  padding: 16px;
  border-radius: 12px;
  background-color: ${props => props.isUser ? props.theme.userMessageBg : props.theme.aiMessageBg};
  color: ${props => props.theme.text};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: relative;
  max-width: 90%;
  ${props => props.isUser ? 'margin-left: auto;' : ''}
  transition: background-color 0.3s ease, color 0.3s ease;
`;

const MessageHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 8px;
`;

const Avatar = styled.div<{ isUser: boolean }>`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: ${props => props.isUser ? props.theme.primary : '#10b981'};
  margin-right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
`;

const MessageText = styled.div`
  line-height: 1.5;
  white-space: pre-wrap;
  
  /* Styling for markdown elements */
  strong {
    font-weight: 600;
  }
  
  em {
    font-style: italic;
  }
  
  h1, h2, h3 {
    margin: 16px 0 8px;
    font-weight: 600;
  }
  
  h1 {
    font-size: 1.5em;
  }
  
  h2 {
    font-size: 1.3em;
  }
  
  h3 {
    font-size: 1.1em;
  }
  
  pre {
    background-color: ${props => props.theme.background === '#111827' ? '#0f172a' : '#f1f5f9'};
    padding: 12px;
    border-radius: 6px;
    margin: 12px 0;
    overflow-x: auto;
  }
  
  code {
    font-family: monospace;
    font-size: 0.9em;
  }
  
  ul, ol {
    margin: 8px 0;
    padding-left: 24px;
  }
  
  li {
    margin: 4px 0;
  }
  
  a {
    color: ${props => props.theme.primary};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const SourcesContainer = styled.div`
  margin-top: 12px;
  font-size: 12px;
`;

const SourceLink = styled.a`
  color: ${props => props.theme.primary};
  text-decoration: none;
  margin-right: 8px;
  
  &:hover {
    text-decoration: underline;
  }
`;

const StatusIndicator = styled.div<{ isConnected: boolean }>`
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: ${props => props.isConnected ? props.theme.success : props.theme.error};
  margin-left: 10px;
`;

const Footer = styled.footer`
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid ${props => props.theme.border};
  display: flex;
  justify-content: space-between;
  color: ${props => props.theme.secondary};
  font-size: 14px;
`;

const FooterLinks = styled.div`
  display: flex;
  gap: 20px;
`;

const FooterLink = styled.a`
  color: ${props => props.theme.secondary};
  text-decoration: none;
  
  &:hover {
    color: ${props => props.theme.primary};
  }
`;

const EmptyState = styled.div`
  text-align: center;
  color: ${props => props.theme.secondary};
  padding: 60px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
`;

const EmptyStateIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: ${props => props.theme.background === '#111827' ? '#1f2937' : '#f3f4f6'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
`;

const EmptyStateTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: ${props => props.theme.text};
`;

const EmptyStateText = styled.p`
  font-size: 14px;
  max-width: 400px;
  margin: 0 auto;
`;

// Utility function to safely parse markdown
const parseMarkdown = (text: string): string => {
  if (!text) return '';
  
  // Process code blocks first to avoid conflicts
  let processed = text
    // Code blocks
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    
    // Bold - handle text with parentheses inside bold formatting
    .replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>')
    
    // Italic
    .replace(/\*([\s\S]*?)\*/g, '<em>$1</em>')
    
    // Horizontal rule
    .replace(/^([-=])\1{2,}$/gm, '<hr>')
    
    // Emojis - preserve them
    .replace(/([🏀📊📈🔥⚡️🌟✨⭐️])/g, '<span style="font-size: 1.2em;">$1</span>')
    
    // Headers
    .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
    .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
    .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
    
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: #2563eb; text-decoration: none;">$1</a>')
    
    // Blockquotes
    .replace(/^>\s+(.*?)$/gm, '<blockquote>$1</blockquote>');
  
  // Handle line breaks before list processing to avoid gaps
  processed = processed
    // Convert double line breaks to a special marker
    .replace(/\n\n/g, '<br class="paragraph-break">')
    // Convert single line breaks to a different marker
    .replace(/\n/g, '<br class="line-break">');
  
  // Special handling for projection-style formatting
  processed = processed
    // Make headers and section titles stand out
    .replace(/<br class="line-break">(📊.*?📊)<br class="line-break">/g, 
      '<div style="font-size: 1.3em; font-weight: bold; color: #4f46e5; margin: 10px 0; text-align: center;">$1</div>')
    
    .replace(/<br class="line-break">(🏀.*?:)<br class="line-break">/g, 
      '<div style="font-size: 1.1em; font-weight: bold; color: #2563eb; margin: 8px 0 4px 0;">$1</div>')
    
    .replace(/<br class="line-break">(📈.*?:)<br class="line-break">/g, 
      '<div style="font-size: 1.1em; font-weight: bold; color: #059669; margin: 8px 0 4px 0;">$1</div>')
    
    // Format stat categories with proper spacing
    .replace(/<br class="line-break">\s*([A-Z]+):\s*<br class="line-break">/g, 
      '<div style="font-weight: bold; color: #4b5563; margin: 8px 0 4px 0;">$1:</div>')
    
    // Improved list handling - convert bullet points to styled divs
    .replace(/(<br class="line-break">)\s*[•-]\s+(.*?)(?=<br class="line-break">|$)/g, 
      '<div style="display: flex; margin: 4px 0 4px 12px;"><span style="margin-right: 8px;">•</span><span>$2</span></div>')
    
    // Improve stat line formatting with specific pattern for projections
    .replace(/(<br class="line-break">)\s*•\s+([\d.]+)\s+-\s+(.*?)(?=<br class="line-break">|$)/g, 
      '<div style="display: flex; margin: 4px 0 4px 12px;"><span style="font-weight: bold; min-width: 50px;">$2</span><span>$3</span></div>')
    
    // Format stat categories
    .replace(/(POINTS|REBOUNDS|ASSISTS|STEALS|BLOCKS|THREE POINTERS):/g, 
      '<div style="font-weight: bold; color: #4b5563; margin: 8px 0 4px 0;">$1:</div>');
  
  // Convert the special markers back to appropriate HTML
  processed = processed
    .replace(/<br class="paragraph-break">/g, '<div style="margin: 12px 0;"></div>')
    .replace(/<br class="line-break">/g, '<div style="margin: 2px 0;"></div>');
  
  return processed;
};

// Simple HTML sanitizer to prevent XSS attacks
const sanitizeHtml = (html: string): string => {
  // Create a new div element
  const tempDiv = document.createElement('div');
  // Set the HTML content with the provided value
  tempDiv.innerHTML = html;
  
  // Return the cleaned HTML
  return tempDiv.innerHTML;
};

interface MessageType {
  text: string;
  isUser: boolean;
  timestamp: number;
  sources?: string[];
}

const App: React.FC = () => {
  const { colors } = useTheme();
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Generate a random session ID if not already stored
  const getSessionId = useCallback(() => {
    let sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
      sessionId = Math.random().toString(36).substring(2, 15);
      localStorage.setItem('chatSessionId', sessionId);
    }
    return sessionId;
  }, []);

  // Test markdown parsing
  useEffect(() => {
    // This is just for development testing, can be removed in production
    console.log('Testing markdown parsing:');
    const testCases = [
      '**Jordi Alba (Charlotte)**',
      '*Italic text*',
      '**Bold with (parentheses) inside**',
      '# Header 1',
      '[Link](https://example.com)'
    ];
    
    testCases.forEach(test => {
      console.log(`Original: ${test}`);
      console.log(`Parsed: ${parseMarkdown(test)}`);
    });
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = useCallback(() => {
    const sessionId = getSessionId();
    // Use the user's WebSocket URL format with the session ID
    const websocket = new WebSocket(`ws://localhost:8765/ws/${sessionId}`);

    websocket.onopen = () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
    };

    websocket.onclose = () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    websocket.onmessage = (event) => {
      setIsLoading(false);
      try {
        const data = JSON.parse(event.data);
        const newMessage: MessageType = {
          text: data.text || data.message || event.data,
          isUser: false,
          timestamp: Date.now(),
          sources: data.sources || []
        };
        setMessages(prev => [...prev, newMessage]);
      } catch (error) {
        // If not JSON, just use the raw data
        const newMessage: MessageType = {
          text: event.data,
          isUser: false,
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, newMessage]);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsLoading(false);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [getSessionId]);

  useEffect(() => {
    connectWebSocket();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [connectWebSocket]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !ws || !isConnected) return;

    const newMessage: MessageType = {
      text: inputValue,
      isUser: true,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);
    ws.send(JSON.stringify({ query: inputValue }));
    setInputValue('');
  };

  const formatMessageText = (text: string) => {
    // First parse markdown
    let formattedText = parseMarkdown(text);
    
    // Then convert plain URLs to clickable links (for URLs not already in markdown format)
    const urlRegex = /(?<!["'])(?<!href=")(https?:\/\/[^\s<]+)(?![^<]*>|[^<>]*<\/a>)/g;
    formattedText = formattedText.replace(urlRegex, (url) => 
      `<a href="${url}" target="_blank" rel="noopener noreferrer" style="color: #2563eb; text-decoration: none;">${url}</a>`
    );
    
    // Sanitize the HTML to prevent XSS attacks
    return sanitizeHtml(formattedText);
  };

  return (
    <AppContainer theme={colors}>
      <Header theme={colors}>
        <Logo theme={colors}>
          <LogoIcon theme={colors} />
          AI Chatbot
        </Logo>
        <NavLinks>
          <NavLink href="#" theme={colors}>Home</NavLink>
          <NavLink href="#" theme={colors}>Discover</NavLink>
          <NavLink href="#" theme={colors}>About</NavLink>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ fontSize: '14px', marginRight: '4px' }}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            <StatusIndicator isConnected={isConnected} theme={colors} />
          </div>
          <ThemeToggle />
        </NavLinks>
      </Header>

      <MainContent>
        <form onSubmit={handleSubmit}>
          <SearchContainer>
            <SearchInput
              type="text"
              placeholder="What do you want to know?"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={!isConnected}
              theme={colors}
            />
            <SearchButton 
              type="submit" 
              disabled={!isConnected || !inputValue.trim()}
              theme={colors}
            >
              Ask
            </SearchButton>
          </SearchContainer>
        </form>

        <MessageContainer theme={colors}>
          {messages.length === 0 ? (
            <EmptyState theme={colors}>
              <EmptyStateIcon theme={colors}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path 
                    d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" 
                    stroke={colors.secondary} 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                  <path 
                    d="M9.09 9C9.3251 8.33167 9.78915 7.76811 10.4 7.40913C11.0108 7.05016 11.7289 6.91894 12.4272 7.03871C13.1255 7.15849 13.7588 7.52152 14.2151 8.06353C14.6713 8.60553 14.9211 9.29152 14.92 10C14.92 12 11.92 13 11.92 13" 
                    stroke={colors.secondary} 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                  <path 
                    d="M12 17H12.01" 
                    stroke={colors.secondary} 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                </svg>
              </EmptyStateIcon>
              <EmptyStateTitle theme={colors}>Ask me anything</EmptyStateTitle>
              <EmptyStateText>
                I can search the web and provide answers with sources. Try asking about AI, technology, science, or anything you're curious about.
              </EmptyStateText>
            </EmptyState>
          ) : (
            <>
              {messages.map((message, index) => (
                <Message key={message.timestamp + index} isUser={message.isUser} theme={colors}>
                  <MessageHeader>
                    <Avatar isUser={message.isUser} theme={colors}>
                      {message.isUser ? 'U' : 'AI'}
                    </Avatar>
                    {message.isUser ? 'You' : 'AI Assistant'}
                  </MessageHeader>
                  <MessageText 
                    dangerouslySetInnerHTML={{ 
                      __html: formatMessageText(message.text) 
                    }} 
                    theme={colors}
                  />
                  
                  {message.sources && message.sources.length > 0 && (
                    <SourcesContainer>
                      Sources:
                      {message.sources.map((source, i) => (
                        <SourceLink key={i} href={source} target="_blank" rel="noopener noreferrer" theme={colors}>
                          [{i + 1}]
                        </SourceLink>
                      ))}
                    </SourcesContainer>
                  )}
                </Message>
              ))}
              
              {isLoading && <LoadingAnimation />}
              <div ref={messagesEndRef} />
            </>
          )}
        </MessageContainer>
      </MainContent>

      <Footer theme={colors}>
        <div>© 2024 AI Chatbot</div>
        <FooterLinks>
          <FooterLink href="#" theme={colors}>Privacy</FooterLink>
          <FooterLink href="#" theme={colors}>Terms</FooterLink>
          <FooterLink href="#" theme={colors}>Contact</FooterLink>
        </FooterLinks>
      </Footer>
    </AppContainer>
  );
};

export default App; 