import { spawn } from 'child_process';
import { remoteUser, remoteHost, remoteScriptPath } from './constants.js';

/**
 * Encodes a JSON object to a base64 string.
 * @param {Object} data - The data to encode.
 * @returns {string} Base64-encoded string.
 */
export function encodePayloadToBase64(data) {
  return Buffer.from(JSON.stringify(data)).toString('base64');
}

/**
 * Spawns an SSH process to remotely execute the Python GPIO controller.
 * @param {string} encodedPayload - Base64-encoded JSON payload.
 * @returns {Promise<{ stdout: string, stderr: string, code: number }>}
 */
export function runRemoteScript(encodedPayload) {
  return new Promise((resolve) => {
    const sshArgs = [
      `${remoteUser}@${remoteHost}`,
      `python3 ${remoteScriptPath} ${encodedPayload}`,
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