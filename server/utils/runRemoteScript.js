import { spawn } from 'child_process';
import {
  remoteUser,
  remoteHost,
  remoteScriptPath,
  remoteStopScriptPath,
} from '../constants.js';


/**
 * Spawns an SSH process to remotely execute the Python GPIO controller.
 * @param {string} type - Command type.
 * @param {string} encodedPayload - Base64-encoded JSON payload.
 * @returns {Promise<{ stdout: string, stderr: string, code: number }>}
 */
export function runRemoteScript(type, encodedPayload) {
  const scriptPath = type === 'stop' ? remoteStopScriptPath : remoteScriptPath;
  const commandParts = [`python3 ${scriptPath}`];

  // Add payload if provided
  if (encodedPayload) {
    commandParts.push(`"${encodedPayload}"`);
  }

  return new Promise((resolve) => {
    const sshArgs = [
      `${remoteUser}@${remoteHost}`,
      commandParts.join(' ')
    ];

    console.log(`Spawning SSH process: ssh ${sshArgs.join(' ')}`);
    const sshProcess = spawn('ssh', sshArgs);

    let stdoutData = '';
    let stderrData = '';

    sshProcess.stdout.on('data', (data) => {
      const text = data.toString();
      stdoutData += text;
      process.stdout.write(`[SSH STDOUT] ${text}`);
    });

    sshProcess.stderr.on('data', (data) => {
      const text = data.toString();
      stderrData += text;
      process.stderr.write(`[SSH STDERR] ${text}`);
    });

    sshProcess.on('close', (code) => {
      resolve({ stdout: stdoutData, stderr: stderrData, code });
    });
  });
}
