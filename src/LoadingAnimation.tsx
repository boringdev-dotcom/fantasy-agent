import React from 'react';
import styled, { keyframes } from 'styled-components';
import { useTheme } from './ThemeContext';

const rotate = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const pulse = keyframes`
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const Spinner = styled.div`
  position: relative;
  width: 24px;
  height: 24px;
  animation: ${rotate} 1.5s linear infinite;
`;

const Dot = styled.div<{ index: number; color: string }>`
  position: absolute;
  width: 6px;
  height: 6px;
  background-color: ${props => props.color};
  border-radius: 50%;
  top: ${props => {
    switch (props.index) {
      case 0: return '0';
      case 1: return '0';
      case 2: return '50%';
      case 3: return '100%';
      case 4: return '100%';
      case 5: return '50%';
      default: return '0';
    }
  }};
  left: ${props => {
    switch (props.index) {
      case 0: return '50%';
      case 1: return '100%';
      case 2: return '100%';
      case 3: return '50%';
      case 4: return '0';
      case 5: return '0';
      default: return '0';
    }
  }};
  transform: translate(-50%, -50%);
  animation: ${pulse} 1.5s ease-in-out infinite;
  animation-delay: ${props => props.index * 0.25}s;
`;

const LoadingText = styled.div<{ color: string }>`
  margin-left: 12px;
  font-size: 14px;
  color: ${props => props.color};
`;

interface LoadingAnimationProps {
  text?: string;
}

const LoadingAnimation: React.FC<LoadingAnimationProps> = ({ text = "Searching for answers..." }) => {
  const { colors } = useTheme();
  
  return (
    <LoadingContainer>
      <Spinner>
        {[...Array(6)].map((_, i) => (
          <Dot key={i} index={i} color={colors.primary} />
        ))}
      </Spinner>
      <LoadingText color={colors.secondary}>{text}</LoadingText>
    </LoadingContainer>
  );
};

export default LoadingAnimation; 