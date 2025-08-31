import { logger } from '../../utils/logger.js';

/**
 * Returns all archived logs for a given operation.
 * 
 * - Reads logs from disk asynchronously.
 * - Responds with JSON: { operationId, logs: [] }.
 * - Handles errors gracefully.
 */
export const getLogs = async (req, res) => {
  const { operationId } = req.params;

  // Allow cross-origin requests (CORS)
  res.setHeader('Access-Control-Allow-Origin', '*'); // TODO: remove in production

  try {
    // Read logs asynchronously
    const logs = await logger.read(operationId);

    // Respond with logs
    return res.status(200).json({ operationId, logs });
  } catch (err) {
    console.error(`Failed to read logs for operation ${operationId}:`, err);

    // Respond with 500 Internal Server Error if something goes wrong
    return res.status(500).json({
      error: `Failed to read logs for operation ${operationId}`,
    });
  }
};
