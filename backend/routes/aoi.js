const express = require('express')
const router = express.Router()
const aoiController = require('../controllers/aoiController')
const app = express();

router.post('/submit', aoiController.submitAOI)


// NEW Route for starting the robust monitoring
router.post('/monitor', aoiController.startMonitoring)
// app.post('/api/aoi/test-local', aoiController.runLocalTest);
router.post('/monitor/stop', aoiController.stopMonitoring)
router.get('/download/:filename', aoiController.downloadFile);
module.exports = router

