import { Router } from "express";
import { operateValves } from "../controllers/index.js";

const router = Router();

router.route('/api/valves/operate').post(operateValves);

export default router; 