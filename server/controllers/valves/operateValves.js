import { toBase64, runRemoteScript } from '../../utils/index.js';

/**
 * Controller to activate GPIO pins remotely via SSH.
 * Expects a JSON body, encodes it to base64, and runs a remote Python script over SSH.
 */
export const operateValves = async (req, res) => {
  try {
    const encodedPayload = toBase64(req.body);

    const operationId = Date.now().toString(); // TODO: Use UUIDs
    const log = {
      id: operationId,
      date: new Date().toLocaleDateString('en-GB'),
      time: new Date().toLocaleTimeString(),
    }
    console.log('Operation details:', log); // TODO: save in DB

    const { stdout, stderr, code } = await runRemoteScript(
      'start',
      encodedPayload,
      operationId
    );

    if (code !== 0) {
      console.error(`SSH process exited with code ${code}`);
      return res.status(500).json({ error: stderr || `Exit code ${code}` });
    }

    return res.json({ success: true, output: stdout, operationId });
  } catch (error) {
    console.error(`Unexpected error during activation: ${error.message}`);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
