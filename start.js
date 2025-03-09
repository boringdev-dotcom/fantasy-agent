const { spawn } = require('child_process');
const os = require('os');

// Determine the correct command based on OS
const isWindows = os.platform() === 'win32';
const npmCmd = isWindows ? 'npm.cmd' : 'npm';

console.log('Starting AI Chatbot application...');

// Start the React client
const client = spawn(npmCmd, ['start'], {
  stdio: 'inherit',
  shell: true
});

// Handle process termination
const cleanup = () => {
  console.log('\nShutting down...');
  client.kill();
  process.exit(0);
};

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

console.log('Client is running!');
console.log('Press Ctrl+C to stop the process.');

// Handle errors
client.on('error', (error) => {
  console.error('Client error:', error);
  cleanup();
});

// Handle process exit
client.on('exit', (code) => {
  if (code !== 0 && code !== null) {
    console.error(`Client process exited with code ${code}`);
    cleanup();
  }
}); 