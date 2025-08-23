const express = require('express')
const cors = require('cors')
const path = require('path');
const bodyParser = require('body-parser')
const nodemailer = require('nodemailer');
require('dotenv').config({ path: path.join(__dirname, '.env') });

const app = express()
app.use(cors())
app.use(bodyParser.json())

// Serve static files from the 'temp_downloads' directory under a new /api/images route
// The path.join ensures this works correctly on all operating systems
app.use('/api/images', express.static(path.join(__dirname, '..', 'processing', 'temp_downloads')));

const { EMAIL_USER, EMAIL_PASSWORD, ALERT_RECIPIENT } = process.env;
if (!EMAIL_USER || !EMAIL_PASSWORD) {
    console.error('Missing EMAIL_USER or EMAIL_PASSWORD in environment. Email alerts will be disabled.');
} else {
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: EMAIL_USER,
            pass: EMAIL_PASSWORD,
        },
    });
    app.locals.transporter = transporter;
    app.locals.alertRecipient = ALERT_RECIPIENT;
    console.log('Nodemailer transporter initialized.');
}

const aoiRoutes = require('./routes/aoi')
app.use('/api/aoi', aoiRoutes)

const PORT = 5000
app.listen(PORT, () => console.log(`Backend running on port ${PORT}`))


















// const express = require('express')
// const cors = require('cors')
// const path = require('path');
// const bodyParser = require('body-parser')
// const nodemailer = require('nodemailer'); // NEW
// require('dotenv').config({ path: path.join(__dirname, '.env') }); // New import
// const app = express()
// app.use(cors())
// app.use(bodyParser.json())


// const { EMAIL_USER, EMAIL_PASSWORD, ALERT_RECIPIENT } = process.env;
// if (!EMAIL_USER || !EMAIL_PASSWORD) {
//     console.error('Missing EMAIL_USER or EMAIL_PASSWORD in environment. Email alerts will be disabled.');
// } else {
//     const transporter = nodemailer.createTransport({
//         service: 'gmail',
//         auth: {
//             user: EMAIL_USER,
//             pass: EMAIL_PASSWORD,
//         },
//     });
//     // Attach transporter to the request object so it's available in controllers
//     app.locals.transporter = transporter;
//     app.locals.alertRecipient = ALERT_RECIPIENT;
//     console.log('Nodemailer transporter initialized.');
// }

// const aoiRoutes = require('./routes/aoi')
// app.use('/api/aoi', aoiRoutes)




// const PORT = 5000
// app.listen(PORT, () => console.log(`Backend running on port ${PORT}`))






