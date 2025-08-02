import dotenv from 'dotenv';
dotenv.config();

export const remoteUser = process.env.SSH_USER;
export const remoteHost = process.env.SSH_HOST;
export const remoteScriptPath = process.env.SCRIPT_PATH;