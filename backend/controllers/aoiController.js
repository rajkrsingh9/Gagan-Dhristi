const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const nodemailer = require('nodemailer');
require('dotenv').config({ path: path.join(__dirname, '.env') });


//const PYTHON_PATH = 'C:\\Users\\unnat\\venv\\Scripts\\python.exe';
//const PYTHON_PATH = 'C:\\Users\\user\\venv\\Scripts\\python.exe';
const PYTHON_PATH = 'C:\\Users\\user\\venv\\Scripts\\python.exe'
const TEMP_DOWNLOADS_DIR = path.join(__dirname, '../../../processing/temp_downloads');
const { EMAIL_USER, ALERT_RECIPIENT } = process.env;











// // Helper function to run Python scripts
// const runPythonScript = (scriptName, args) => {
//     return new Promise((resolve, reject) => {
//         const scriptPath = path.join(__dirname, '../../processing', scriptName);
//         const python = spawn(PYTHON_PATH, [scriptPath, ...args]);
        
//         let data = '';
//         let errorData = '';

//         python.stdout.on('data', (chunk) => {
//             data += chunk.toString();
//         });

//         python.stderr.on('data', (chunk) => {
//             errorData += chunk.toString();
//         });

//         python.on('close', (code) => {
//             if (code === 0) {
//                 try {
//                     const lines = data.trim().split('\n');
//                     let lastLine = '';
//                     for (let i = lines.length - 1; i >= 0; i--) {
//                         if (lines[i].startsWith('{') && lines[i].endsWith('}')) {
//                             lastLine = lines[i];
//                             break;
//                         }
//                     }
//                     if (!lastLine) {
//                         console.error(`No valid JSON output from ${scriptName}. Full Output:`, data);
//                         return resolve({ status: 'success', message: 'Script completed with no output.', details: data });
//                     }
//                     const result = JSON.parse(lastLine);
//                     resolve(result);
//                 } catch (jsonErr) {
//                     console.error(`Failed to parse JSON from ${scriptName}:`, jsonErr, 'Full Output:', data);
//                     reject({ status: 'error', message: `Failed to parse output from ${scriptName}.`, details: data });
//                 }
//             } else {
//                 console.error(`Python script ${scriptName} exited with code ${code}. Error output: ${errorData}`);
//                 reject({ status: 'error', message: `Processing failed for ${scriptName}.`, details: errorData });
//             }
//         });
//     });
// };
// Helper function to run Python scripts
const runPythonScript = (scriptName, args) => {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(__dirname, '../../processing', scriptName);
        const python = spawn(PYTHON_PATH, [scriptPath, ...args]);
        
        let data = '';
        let errorData = '';

        python.stdout.on('data', (chunk) => {
            data += chunk.toString();
        });

        python.stderr.on('data', (chunk) => {
            errorData += chunk.toString();
        });

        python.on('close', (code) => {
            if (code === 0) {
                try {
                    const lines = data.trim().split('\n');
                    let lastLine = '';
                    for (let i = lines.length - 1; i >= 0; i--) {
                        if (lines[i].startsWith('{') && lines[i].endsWith('}')) {
                            lastLine = lines[i];
                            break;
                        }
                    }
                    if (!lastLine) {
                        console.error(`No valid JSON output from ${scriptName}. Full Output:`, data);
                        return resolve({ status: 'success', message: 'Script completed with no output.', details: data });
                    }
                    const result = JSON.parse(lastLine);
                    resolve(result);
                } catch (jsonErr) {
                    console.error(`Failed to parse JSON from ${scriptName}:`, jsonErr, 'Full Output:', data);
                    reject({ status: 'error', message: `Failed to parse output from ${scriptName}.`, details: data });
                }
            } else {
                console.error(`Python script ${scriptName} exited with code ${code}. Error output: ${errorData}`);
                reject({ status: 'error', message: `Processing failed for ${scriptName}.`, details: errorData });
            }
        });
    });
};




// const sendAlertEmail = async (transporter, recipient, changeDetails) => {
//     if (!transporter || !recipient) {
//         console.warn('Email transporter not configured or recipient missing. Skipping email alert.');
//         return;
//     }

//     const { combined_change, threshold, aoi_name = 'Unnamed AOI', ndvi_change, unet_change, unet_change_overlay_path, unet_change_only_path } = changeDetails;
//     const subject = `Significant Change Alert for AOI: ${aoi_name}`;

//     let changeList = '';
//     let attachments = [];

//     if (ndvi_change !== undefined) {
//         changeList += `<li><strong>Vegetation & Land Cover Change:</strong> ${ndvi_change.toFixed(2)}%</li>`;
//     }
//     if (unet_change !== undefined) {
//         changeList += `<li><strong>Structural & Ground-Level Change:</strong> ${unet_change.toFixed(2)}%</li>`;
//         if (unet_change_overlay_path && fs.existsSync(path.join(TEMP_DOWNLOADS_DIR, unet_change_overlay_path))) {
//             attachments.push({
//                 filename: 'change_overlay.png',
//                 path: path.join(TEMP_DOWNLOADS_DIR, unet_change_overlay_path)
//             });
//         }
//         if (unet_change_only_path && fs.existsSync(path.join(TEMP_DOWNLOADS_DIR, unet_change_only_path))) {
//             attachments.push({
//                 filename: 'changes_only.png',
//                 path: path.join(TEMP_DOWNLOADS_DIR, unet_change_only_path)
//             });
//         }
//     }


//     const htmlBody = `
//         <h2>Significant Change Detected!</h2>
//         <p>Change has been detected in a user-defined Area of Interest. The change was significant enough to exceed your set threshold.</p>
        
//         <h3>Summary of Changes</h3>
//         <ul>
//             <li><strong>Combined Change Score:</strong> ${combined_change.toFixed(2)}%</li>
//             ${changeList}
//         </ul>
        
//         <p><b>Your set threshold for this alert was:</b> ${threshold.toFixed(2)}%</p>
        
//         <h3>Change Detection Models Used:</h3>
//         <ul>
//             <li><b>Vegetation & Land Cover Change (NDVI):</b> Detects changes in greenness and plant health.</li>
//             <li><b>Structure & Ground Level Change (Siamese U-Net):</b> Detects physical alterations like new buildings, roads, or land clearing. This is the model that generated the attached visualization.</li>
//         </ul>
        
//         <p>You can find the visualization of the detected structural changes attached to this email:</p>
//         <ul>
//             <li><b>change_overlay.png:</b> The new image with detected changes highlighted in red.</li>
//             <li><b>changes_only.png:</b> An image showing only the detected changes on a black background.</li>
//         </ul>
//         <p>Time of Detection: ${new Date().toLocaleString()}</p>
//     `;

//     const mailOptions = {
//         from: `"Change Detection Alert" <${EMAIL_USER}>`,
//         to: recipient,
//         subject: subject,
//         html: htmlBody,
//         attachments: attachments,
//     };

//     try {
//         await transporter.sendMail(mailOptions);
//         console.log('Email alert sent successfully with attachments.');
//     } catch (error) {
//         console.error('Failed to send email alert:', error);
//     }
// };





// Function to send the alert email
const sendAlertEmail = async (transporter, recipient, changeDetails) => {
    if (!transporter || !recipient) {
        console.warn('Email transporter not configured or recipient missing. Skipping email alert.');
        return;
    }

    const { combined_change, threshold, aoi_name = 'Unnamed AOI', ndvi_change, unet_change } = changeDetails;
    const subject = `Significant Change Alert for AOI: ${aoi_name}`;

    let changeList = '';
    if (ndvi_change !== undefined) {
      changeList += `<li><strong>Vegetation & Land Cover Change:</strong> ${ndvi_change.toFixed(2)}%</li>`;
    }
    if (unet_change !== undefined) {
      changeList += `<li><strong>Structural & Ground-Level Change:</strong> ${unet_change.toFixed(2)}%</li>`;
    }


    const htmlBody = `
        <h2>Significant Change Detected!</h2>
        <p>Change has been detected in a user-defined Area of Interest.</p>
        <ul>
            <li><strong> Change in AOI :</strong> ${combined_change.toFixed(2)}%</li>
            ${changeList}
            <li><strong>User Threshold:</strong> ${threshold.toFixed(2)}%</li>
            ${changeList}
            <li><strong>Structural & Ground-Level Change:</strong> ${unet_change.toFixed(2)}%</li>

        </ul>
        <p>Time of Detection: ${new Date().toLocaleString()}</p>
    `;

    const mailOptions = {
        from: `"Change Detection Alert" <${EMAIL_USER}>`,
        to: recipient,
        subject: subject,
        html: htmlBody,
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log('Email alert sent successfully.');
    } catch (error) {
        console.error('Failed to send email alert:', error);
    }
};


const MONITORING_TASKS_FILE = path.join(__dirname, '../../processing/monitoring_tasks.json');




// Helper function to read monitoring tasks from a file
const getMonitoringTasks = () => {
    if (!fs.existsSync(MONITORING_TASKS_FILE)) {
        return [];
    }
    const data = fs.readFileSync(MONITORING_TASKS_FILE, 'utf-8');
    return JSON.parse(data);
};



// Helper function to save monitoring tasks to a file
const saveMonitoringTasks = (tasks) => {
    fs.writeFileSync(MONITORING_TASKS_FILE, JSON.stringify(tasks, null, 2));
};




// exports.submitAOI = async (req, res) => {
//     try {
//         const payload = req.body;
//         const { geometry, startDate, endDate, threshold, detectionMethods } = payload;
//         const geojson_str = JSON.stringify(geometry);

//         if (!detectionMethods || detectionMethods.length === 0) {
//             return res.status(400).json({ status: 'error', message: 'No detection method selected.' });
//         }

//         const downloadResult = await runPythonScript('gee_drive_download.py', [
//             geojson_str,
//             startDate,
//             endDate
//         ]);

//         if (downloadResult.status !== 'success') {
//             return res.status(500).json(downloadResult);
//         }
        
//         const t1_path = downloadResult.t1_path;
//         const t2_path = downloadResult.t2_path;
        
//         let ndviResult, unetResult;
//         const promises = [];

//         if (detectionMethods.includes('vegetation')) {
//             promises.push(runPythonScript('gee_change_detection.py', [t1_path, t2_path, threshold]));
//         } else {
//             promises.push(Promise.resolve(null));
//         }

//         if (detectionMethods.includes('structural')) {
//             promises.push(runPythonScript('unet_inference.py', [t1_path, t2_path]));
//         } else {
//             promises.push(Promise.resolve(null));
//         }

//         [ndviResult, unetResult] = await Promise.all(promises);

//         const finalResponse = {
//             status: 'success',
//             message: "Change detection tasks completed.",
//             ndvi_summary: ndviResult ? {
//                 // ... (your existing ndvi summary)
//                 message: ndviResult.message,
//                 total_aoi_area_ha: ndviResult.total_aoi_area_ha,
//                 gain_area_ha: ndviResult.gain_area_ha,
//                 loss_area_ha: ndviResult.loss_area_ha,
//                 percentage_change: ndviResult.percentage_change
//             } : null,
//             unet_summary: unetResult ? {
//                 message: unetResult.message,
//                 percentage_change: unetResult.percentage_change,
//                 total_change_pixels: unetResult.total_change_pixels,
//                 change_mask_path: unetResult.change_mask_path, // GeoTIFF
//                 change_overlay_png: unetResult.change_overlay_png, // New PNG
//                 change_only_png: unetResult.change_only_png        // New PNG
//             } : null
//         };
        
//         let combinedChange = 0;
//         let changeCount = 0;

//         if (finalResponse.ndvi_summary) {
//             combinedChange += finalResponse.ndvi_summary.percentage_change;
//             changeCount++;
//         }
//         if (finalResponse.unet_summary) {
//             combinedChange += finalResponse.unet_summary.percentage_change;
//             changeCount++;
//         }
//         if (changeCount > 0) {
//             combinedChange = combinedChange / changeCount;
//         }

//         console.log(`Combined Change: ${combinedChange}%`);
//         console.log(`Threshold: ${parseFloat(payload.threshold) * 100}%`);
//         console.log(`Comparison result: ${combinedChange > parseFloat(payload.threshold) * 100}`);

//         if (combinedChange > parseFloat(payload.threshold) * 100) {
//             const changeDetails = {
//                 aoi_name: 'User-defined AOI',
//                 ndvi_change: finalResponse.ndvi_summary ? finalResponse.ndvi_summary.percentage_change : undefined,
//                 unet_change: finalResponse.unet_summary ? finalResponse.unet_summary.percentage_change : undefined,
//                 combined_change: combinedChange,
//                 threshold: parseFloat(payload.threshold) * 100,
//                 // Pass the new PNG paths to the email function
//                 unet_change_overlay_path: finalResponse.unet_summary ? finalResponse.unet_summary.change_overlay_png : undefined,
//                 unet_change_only_path: finalResponse.unet_summary ? finalResponse.unet_summary.change_only_png : undefined,
//             };
//             const { transporter, alertRecipient } = req.app.locals;
//             sendAlertEmail(transporter, alertRecipient, changeDetails);
//         }

//         res.json(finalResponse);
//         console.log('Successfully processed AOI request. Combined response sent to frontend.');
        
//     } catch (err) {
//         console.error("Server error:", err);
//         if (err && err.status === 'error') {
//             res.status(500).json(err);
//         } else {
//             res.status(500).json({ status: 'error', message: 'An internal server error occurred.' });
//         }
//     }
// };






exports.submitAOI = async (req, res) => {
    try {
        const payload = req.body;
        const { geometry, startDate, endDate, threshold, detectionMethods, userEmail } = payload;
        const geojson_str = JSON.stringify(geometry);

        // Input validation for detection methods
        if (!detectionMethods || detectionMethods.length === 0) {
            return res.status(400).json({ status: 'error', message: 'No detection method selected.' });
        }

        const downloadResult = await runPythonScript('gee_drive_download.py', [
            geojson_str,
            startDate,
            endDate
        ]);

        if (downloadResult.status !== 'success') {
            return res.status(500).json(downloadResult);
        }
        
        const t1_path = downloadResult.t1_path;
        const t2_path = downloadResult.t2_path;
        
        let ndviResult, unetResult;
        const promises = [];

        if (detectionMethods.includes('vegetation')) {
            promises.push(runPythonScript('gee_change_detection.py', [t1_path, t2_path, threshold]));
        } else {
            promises.push(Promise.resolve(null));
        }

        if (detectionMethods.includes('structural')) {
            promises.push(runPythonScript('unet_inference.py', [t1_path, t2_path]));
        } else {
            promises.push(Promise.resolve(null));
        }

        [ndviResult, unetResult, cvaResult] = await Promise.all(promises);

        const finalResponse = {
            status: 'success',
            message: "Change detection tasks completed.",
            ndvi_summary: ndviResult ? ndviResult.summary : null,
            unet_summary: unetResult ? {
                message: unetResult.message,
                percentage_change: unetResult.percentage_change,
                total_change_pixels: unetResult.total_change_pixels,
                change_mask_path: unetResult.change_mask_path
            } : null,
            cva_summary: cvaResult ? cvaResult.summary : null
        };
        
        let combinedChange = 0;
        let changeCount = 0;

        if (finalResponse.ndvi_summary) {
            combinedChange += finalResponse.ndvi_summary.percentage_change;
            changeCount++;
        }
        if (finalResponse.unet_summary) {
            combinedChange += finalResponse.unet_summary.percentage_change;
            changeCount++;
        }
if (finalResponse.cva_summary) {
        combinedChange += finalResponse.cva_summary.percentage_change;
        changeCount++;
    }
        if (changeCount > 0) {
            combinedChange = combinedChange / changeCount;
        }

        // Log the values for debugging
        console.log(`Combined Change: ${combinedChange}%`);
        console.log(`Threshold: ${parseFloat(payload.threshold) * 100}%`);
        console.log(`Comparison result: ${combinedChange > parseFloat(payload.threshold) * 100}`);

        if (combinedChange > parseFloat(payload.threshold) * 100) {
            const changeDetails = {
                aoi_name: 'User-defined AOI',
                ndvi_change: finalResponse.ndvi_summary ? finalResponse.ndvi_summary.percentage_change : undefined,
                unet_change: finalResponse.unet_summary ? finalResponse.unet_summary.percentage_change : undefined,
                combined_change: combinedChange,
                threshold: parseFloat(payload.threshold) * 100, // Pass the percentage value for the email
            };
            const { transporter, alertRecipient } = req.app.locals;
            const recipient = userEmail || alertRecipient;
            sendAlertEmail(transporter, recipient, changeDetails);
        }

        res.json(finalResponse);
        console.log('Successfully processed AOI request. Combined response sent to frontend.');
        
    } catch (err) {
        console.error("Server error:", err);
        if (err && err.status === 'error') {
            res.status(500).json(err);
        } else {
            res.status(500).json({ status: 'error', message: 'An internal server error occurred.' });
        }
    }
};


exports.startMonitoring = async (req, res) => {
    // FIX: Add 'userEmail' to the destructuring assignment
    const { geometry, monitoringInterval, threshold, userEmail } = req.body; 
    
    if (!userEmail) {
        return res.status(400).json({ status: 'error', message: 'Email recipient is required for monitoring.' });
    }

    const aoiId = `aoi-${Date.now()}`;
    
    const newTask = {
        aoi_id: aoiId,
        geojson: geometry,
        monitoring_interval_days: monitoringInterval,
        threshold: threshold,
        last_checked_date: null,
        email_recipient: userEmail, 
    };

    try {
        const tasks = getMonitoringTasks();
        tasks.push(newTask);
        saveMonitoringTasks(tasks);

        const pythonProcess = spawn(PYTHON_PATH, [path.join(__dirname, '../../processing/monitoring_scheduler.py')]);

        pythonProcess.stdout.on('data', (data) => {
            console.log(`Python Monitoring: ${data}`);
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Python Monitoring Error: ${data}`);
        });

        res.status(200).json({ status: 'success', message: 'Monitoring started successfully. The system will now check for changes periodically.' });
    } catch (err) {
        console.error("Failed to start monitoring:", err);
        res.status(500).json({ status: 'error', message: 'Failed to start monitoring process.' });
    }
};


exports.stopMonitoring = (req, res) => {
    try {
        // Clear the monitoring tasks file by writing an empty array
        saveMonitoringTasks([]);
        console.log('All monitoring tasks have been cleared.');
        res.status(200).json({ status: 'success', message: 'Monitoring has been stopped. No further alerts will be sent for previous tasks.' });
    } catch (err) {
        console.error('Failed to stop monitoring:', err);
        res.status(500).json({ status: 'error', message: 'Failed to stop monitoring. Check server logs.' });
    }
};


exports.downloadFile = (req, res) => {
    const { filename } = req.params;
    // Sanitize filename to prevent directory traversal attacks
    const safeFilename = path.basename(filename);
    const filePath = path.join(TEMP_DOWNLOADS_DIR, safeFilename);

    if (!fs.existsSync(filePath) || !filePath.startsWith(TEMP_DOWNLOADS_DIR)) {
        return res.status(404).json({ status: 'error', message: 'File not found.' });
    }

    res.download(filePath, (err) => {
        if (err) {
            console.error(`Download error for file ${safeFilename}:`, err);
            res.status(500).send("Error downloading the file.");
        }
    });
};


exports.runLocalTest = async (req, res) => {
    try {
        const { image1Path, image2Path, threshold, detectionMethods } = req.body;

        if (!detectionMethods || detectionMethods.length === 0) {
            return res.status(400).json({ status: 'error', message: 'No detection method selected.' });
        }

        // Use the hardcoded paths directly instead of calling gee_drive_download.py
        const t1_path = path.resolve(__dirname, image1Path);
        const t2_path = path.resolve(__dirname, image2Path);
        
        // Check if the hardcoded files exist
        if (!fs.existsSync(t1_path) || !fs.existsSync(t2_path)) {
            return res.status(404).json({
                status: 'error',
                message: 'One or both hardcoded image files not found.',
                details: `Missing files: ${!fs.existsSync(t1_path) ? t1_path : ''} ${!fs.existsSync(t2_path) ? t2_path : ''}`
            });
        }
        
        let ndviResult, unetResult;
        const promises = [];

        if (detectionMethods.includes('vegetation')) {
            promises.push(runPythonScript('gee_change_detection.py', [t1_path, t2_path, threshold]));
        } else {
            promises.push(Promise.resolve(null));
        }

        if (detectionMethods.includes('structural')) {
            promises.push(runPythonScript('unet_inference.py', [t1_path, t2_path]));
        } else {
            promises.push(Promise.resolve(null));
        }
        // Add the new CVA promise
    if (detectionMethods.includes('cva')) {
        // CVA uses a different script and needs the same paths and threshold
        promises.push(runPythonScript('cva_change_detection.py', [t1_path, t2_path, threshold]));
    } else {
        promises.push(Promise.resolve(null));
    }

        [ndviResult, unetResult, cvaResult] = await Promise.all(promises);

        const finalResponse = {
            status: 'success',
            message: "Local test change detection completed.",
            ndvi_summary: ndviResult ? {
                message: ndviResult.message,
                total_aoi_area_ha: ndviResult.total_aoi_area_ha,
                gain_area_ha: ndviResult.gain_area_ha,
                loss_area_ha: ndviResult.loss_area_ha,
                percentage_change: ndviResult.percentage_change
            } : null,
            unet_summary: unetResult ? {
                message: unetResult.message,
                percentage_change: unetResult.percentage_change,
                total_change_pixels: unetResult.total_change_pixels,
                change_mask_path: unetResult.change_mask_path,
                change_overlay_png: unetResult.change_overlay_png,
                change_only_png: unetResult.change_only_png
            } : null,
            cva_summary: cvaResult ? cvaResult.summary : null
        };

        // You can add the email alert logic here as well if needed.

        res.json(finalResponse);
        console.log('Successfully processed local test request.');
    } catch (err) {
        console.error("Local test server error:", err);
        if (err && err.status === 'error') {
            res.status(500).json(err);
        } else {
            res.status(500).json({ status: 'error', message: 'An internal server error occurred during local test.' });
        }
    }
};

// exports.downloadFile = (req, res) => {
//     const { filename } = req.params;
//     const filePath = path.join(TEMP_DOWNLOADS_DIR, filename);

//     if (!fs.existsSync(filePath) || !filePath.startsWith(TEMP_DOWNLOADS_DIR)) {
//         return res.status(404).json({ status: 'error', message: 'File not found.' });
//     }

//     res.download(filePath, (err) => {
//         if (err) {
//             console.error(`Download error for file ${filename}:`, err);
//             res.status(500).send("Error downloading the file.");
//         }
//     });
// };

