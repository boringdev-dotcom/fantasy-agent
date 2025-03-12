import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

// Define theme types
export type ThemeMode = 'light' | 'dark';

// Define theme colors
export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  cardBackground: string;
  text: string;
  border: string;
  inputBackground: string;
  userMessageBg: string;
  aiMessageBg: string;
  toolCallBg: string;
  toolResultBg: string;
}

// Theme definitions
export const themes: Record<ThemeMode, ThemeColors> = {
  light: {
    primary: '#2563eb',
    secondary: '#64748b',
    background: '#f8fafc',
    cardBackground: '#ffffff',
    text: '#1e293b',
    border: '#e2e8f0',
    inputBackground: '#ffffff',
    userMessageBg: '#e2e8f0',
    aiMessageBg: '#f1f5f9',
    toolCallBg: '#e0f2fe',
    toolResultBg: '#dbeafe'
  },
  dark: {
    primary: '#3b82f6',
    secondary: '#94a3b8',
    background: '#0f172a',
    cardBackground: '#1e293b',
    text: '#f1f5f9',
    border: '#334155',
    inputBackground: '#1e293b',
    userMessageBg: '#334155',
    aiMessageBg: '#1e293b',
    toolCallBg: '#0c4a6e',
    toolResultBg: '#172554'
  }
};

// Create the context
interface ThemeContextType {
  themeMode: ThemeMode;
  colors: ThemeColors;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Create a provider component
interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Check if user has a saved preference or use system preference
  const getSavedTheme = (): ThemeMode => {
    const savedTheme = localStorage.getItem('theme') as ThemeMode;
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      return savedTheme;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  };

  const [themeMode, setThemeMode] = useState<ThemeMode>(getSavedTheme);
  const colors = themes[themeMode];

  // Toggle between light and dark mode
  const toggleTheme = () => {
    setThemeMode(prevMode => {
      const newMode = prevMode === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', newMode);
      return newMode;
    });
  };

  // Update document body background when theme changes
  useEffect(() => {
    document.body.style.backgroundColor = colors.background;
    document.body.style.color = colors.text;
  }, [colors]);

  return (
    <ThemeContext.Provider value={{ themeMode, colors, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use the theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}; 