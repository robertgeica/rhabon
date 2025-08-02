import { toBase64, runRemoteScript } from "../../utils/index.js";


/**
 * Controller to activate GPIO pins remotely via SSH.
 * Expects a JSON body, encodes it to base64, and runs a remote Python script over SSH.
 */
export const operateValves = async (req, res) => {
  try {
    const encodedPayload = toBase64(req.body);

    const { stdout, stderr, code } = await runRemoteScript("start", encodedPayload);

    if (code !== 0) {
      console.error(`SSH process exited with code ${code}`);
      return res.status(500).json({ error: stderr || `Exit code ${code}` });
    }

    return res.json({ success: true, output: stdout });
  } catch (error) {
    console.error(`Unexpected error during activation: ${error.message}`);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
