import dotenv from 'dotenv';
import express from 'express';

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json());

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
