import fs from 'fs';
import path from 'path';

// Resolve absolute path for the "logs" directory
const logsDir = path.resolve('logs');

// Ensure the "logs" directory exists
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

/**
 * Append a message to a log file associated with an operation ID.
 * If the file does not exist, it will be created automatically.
 * Each line will be prefixed with a timestamp.
 * 
 * @param {string} operationId - Unique identifier for the operation
 * @param {string} message - Log message to append
 */

async function write(operationId, message) {

  try {
    const file = path.join(logsDir, `${operationId}.log`);
    const timestamp = new Date().toISOString(); // TODO: Use a more human-friendly format
    await fs.promises.appendFile(file, `[${timestamp}] ${message}\n`); // TODO: Improve format
  } catch (err) {
    console.error(`Failed to append log for ${operationId}:`, err);
  }
}

/**
 * Read all log entries for a given operation ID.
 * Returns an array of strings (each line is one log entry).
 *
 * @param {string} operationId - Unique identifier for the operation
 * @returns {Promise<string[]>} Array of log messages
 */
async function read(operationId) {
  try {
    const file = path.join(logsDir, `${operationId}.log`);
    const exists = await fs.promises
      .access(file, fs.constants.F_OK)
      .then(() => true)
      .catch(() => false);

    if (!exists) return [];

    const data = await fs.promises.readFile(file, "utf-8");
    return data.split("\n").filter(Boolean);
  } catch (err) {
    console.error(`Failed to read log for ${operationId}:`, err);
    return [];
  }
}

export const logger = { write, read };