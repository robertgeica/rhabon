import { runRemoteScript } from "../../utils/index.js";

export const stopValves = async (req, res) => {
  try {
    const { stdout, stderr, code } = await runRemoteScript(
      'stop'
    );
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
