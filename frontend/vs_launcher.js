/**
 * Visual Studio Launcher for Vite
 * 
 * This script acts as a bridge to launch 'npm run dev' from within Visual Studio.
 * It ensures that the process is correctly spawned and output is piped back to VS.
 * 
 * NOTE: Uses ES Module syntax because package.json has "type": "module"
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

console.log('Starting TickerCalTracker Frontend via VS Launcher (ESM)...');

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Determine the npm command based on platform
const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';

// Spawn the npm process
const viteProcess = spawn(npmCmd, ['run', 'dev'], {
    cwd: __dirname,
    stdio: 'inherit', // Pipe output directly to parent (VS Output window)
    shell: true
});

viteProcess.on('error', (err) => {
    console.error('Failed to start frontend process:', err);
    process.exit(1);
});

viteProcess.on('exit', (code) => {
    console.log(`Frontend process exited with code ${code}`);
    process.exit(code);
});

// Open browsers after a short delay to allow servers to start
setTimeout(async () => {
    console.log('Opening Frontend and Backend in browser...');
    const { exec } = await import('child_process');

    // Open Frontend
    exec('start http://localhost:5173');

    // Open Backend Docs
    exec('start http://localhost:5001/docs');
}, 3000);

// Keep the launcher alive to prevent VS from thinking debugging finished immediately
setInterval(() => { }, 1000);
