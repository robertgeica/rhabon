
/**
 * Encodes a JSON object to a base64 string.
 * @param {Object} data - The data to encode.
 * @returns {string} Base64-encoded string.
 */
export function toBase64(data) {
  return Buffer.from(JSON.stringify(data)).toString('base64');
}