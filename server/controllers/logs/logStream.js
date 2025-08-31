import { eventEmitter } from '../../utils/eventEmitter.js';
import { logger } from '../../utils/logger.js';

/**
 * SSE (Server-Sent Events) endpoint to stream operation logs to the frontend.
 * 
 * - Replays past log entries from disk.
 * - Sends live updates emitted via EventEmitter.
 * - Cleans up event listeners when the client disconnects.
 * 
 */
export const logStream = async (req, res) => {
  const { operationId } = req.params;

  // --- Set SSE headers ---
  res.setHeader('Access-Control-Allow-Origin', '*'); // allow CORS TODO: remove in production
  res.setHeader('Content-Type', 'text/event-stream'); // indicate SSE
  res.setHeader('Cache-Control', 'no-cache'); // prevent caching
  res.setHeader('Connection', 'keep-alive'); // keep the HTTP connection open
  res.flushHeaders(); // flush headers immediately so client can start receiving events

  // --- Replay past logs ---
  try {
    const pastLogs = await logger.read(operationId);

    pastLogs.forEach(line => res.write(`data: ${line}\n\n`));
  } catch (err) {
    console.error(`Failed to read past logs for ${operationId}:`, err);
    res.write(`data: ERROR: Failed to read past logs\n\n`);
  }

  // --- Handle live updates ---
  const sendUpdate = (message) => res.write(`data: ${message}\n\n`);

  eventEmitter.on(`statusUpdate:${operationId}`, sendUpdate);

  // --- Cleanup on client disconnect ---
  req.on('close', () => {
    eventEmitter.removeListener(`statusUpdate:${operationId}`, sendUpdate);
  });
};
