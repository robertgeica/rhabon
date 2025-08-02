import dotenv from 'dotenv';
import express from 'express';
import routes from './routes/index.js';

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json());

app.use(routes);

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
