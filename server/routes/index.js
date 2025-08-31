import { Router } from 'express';
import {
  operateValves,
  logStream,
  stopValves,
  getLogs,
} from '../controllers/index.js';

const router = Router();

router.route('/api/valves/operate').post(operateValves);
router.route('/api/valves/stop').post(stopValves);

router.route('/api/logs/:operationId/stream').get(logStream);
router.route('/api/logs/:operationId').get(getLogs);

export default router;
