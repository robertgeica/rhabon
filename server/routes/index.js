import { Router } from "express";
import { operateValves, stopValves } from "../controllers/index.js";

const router = Router();

router.route('/api/valves/operate').post(operateValves);
router.route('/api/valves/stop').post(stopValves);

export default router; 