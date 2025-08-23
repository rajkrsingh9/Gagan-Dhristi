# **Gagan-Dhristi** 🚦🗺️

*An AI-powered Smart Navigation & Traffic Optimization System*

---

## 📌 Project Overview

**Gagan-Dhristi** is an intelligent traffic management and navigation system designed to:

* Provide **shortest route navigation**.
* Detect and display **traffic signals along the route**.
* Enable **emergency vehicle clearance** by dynamically controlling signals.
* Support **real-time monitoring** with change detection for roads and regions of interest.

This project combines **Web, AI/ML, and Geospatial processing** to create smarter cities and safer roads.

---

## ⚙️ Tech Stack

### **Frontend** (Vue.js)

* Vue 3 + Vue CLI
* Components for maps and visualization
* Responsive UI

### **Backend** (Node.js + Express)

* REST APIs for route calculation
* Controller & routing architecture
* Environment-based config

### **Processing (Python)**

* Google Earth Engine (GEE) for change detection
* Custom models (U-Net, CVA)
* Automated monitoring with schedulers

---

## 📂 Project Structure

```plaintext
Gagan-Dhristi/
│── backend/               # Node.js Backend
│   ├── controllers/       # API controllers
│   ├── routes/            # API routes
│   ├── temp_downloads/    # Temporary files (gitignored)
│   ├── .env               # Environment config (gitignored)
│   ├── app.js             # Main backend app
│   └── package.json       # Backend dependencies
│
│── frontend/              # Vue.js Frontend
│   ├── public/            # Public assets
│   ├── src/               # Vue components & assets
│   ├── package.json       # Frontend dependencies
│   ├── vue.config.js      # Vue config
│   └── README.md          # Frontend specific readme
│
│── processing/            # Python scripts for geospatial tasks
│   ├── cva_change_detection.py
│   ├── gee_change_detection.py
│   ├── monitoring_scheduler.py
│   ├── unet_inference.py
│   ├── requirements.txt   # Python dependencies
│   ├── credentials.json   # GEE credentials (gitignored)
│   └── token.json         # Auth token (gitignored)
│
├── .gitignore             # Ignore sensitive/unnecessary files
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/Gagan-Dhristi.git
cd Gagan-Dhristi
```

---

### **2. Backend Setup (Node.js)**

```bash
cd backend
npm install
node app.js
```

Create a `.env` file in `/backend` with your environment variables:

```env
PORT=5000
MONGO_URI=your_mongo_uri_here
API_KEY=your_api_key_here
```

---

### **3. Frontend Setup (Vue.js)**

```bash
cd frontend
npm install
npm run serve
```

---

### **4. Processing Setup (Python)**

```bash
cd processing
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
```

---

## 📊 Features

✔️ Shortest route navigation with real-time alerts
✔️ Traffic signal proximity detection (500m)
✔️ Emergency vehicle clearance system
✔️ Automated monitoring with **GEE + ML models**
✔️ Modular design (backend + frontend + processing)

---

## 🔒 Security & Privacy

* `.env`, API keys, and credentials are **gitignored**.
* Sensitive files (`credentials.json`, `token.json`, `monitoring_tasks.json`) are never pushed.
* Local temp data stored in `backend/temp_downloads/` is excluded.

---

## 🤝 Contributing

Contributions are welcome! Please fork this repo and submit a pull request.

---

## 📜 License

This project is licensed under the **MIT License** – you’re free to use, modify, and distribute with attribution.

---

👉 Pro tip: You can also add **badges** (build status, dependencies, license, etc.) and **screenshots/GIFs** of your UI to make it even more appealing on GitHub.

Do you want me to also create **README.md files for frontend and backend folders separately** (shorter, module-specific ones), so your repo looks super professional?

<!-- 

# Gagan-Dhristi

# frontend

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
cd frontend
npm run serve 

cd backend
node app.js
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).










 -->
