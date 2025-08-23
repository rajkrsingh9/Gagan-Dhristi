# Gagan Dhristi

## 🌍 Change Detection and Monitoring System

A robust, full-stack platform designed to **automatically detect and monitor changes on the Earth's surface** using multi-temporal satellite imagery.  
The system automates the process of comparing two satellite images of the same location, taken at different times, to identify significant changes such as **new construction, deforestation, or land-use shifts**.

---

## 🚀 Key Features

- **Automated Monitoring & Scheduling**  
  A background scheduler continuously monitors user-defined Areas of Interest (AOIs) without manual intervention.

- **Dual-Method Change Detection**
  - **Change Vector Analysis (CVA):** Traditional multi-spectral technique for robust baseline detection.  
  - **Deep Learning (Siamese U-Net):** Modern CNN for granular, pixel-level change identification.

- **Robust Data Pipeline**  
  Handles acquisition & preprocessing of satellite data, intelligently managing issues like cloud cover.

- **Configurable Alerting**  
  Alerts triggered when detected changes exceed a user-defined threshold.

- **High-Performance Processing**  
  Efficient numerical operations on large datasets using specialized libraries.

---

## 🛠️ Technology Stack

**Backend (Python 3.9+)**
- [PyTorch](https://pytorch.org/) → Deep learning inference  
- [rasterio](https://rasterio.readthedocs.io/) & [numpy](https://numpy.org/) → Geospatial & numerical processing  
- [schedule](https://schedule.readthedocs.io/) → Lightweight task scheduling  
- `subprocess` → Orchestration of analysis scripts  

**Backend API**
- [Node.js](https://nodejs.org/) → API layer to handle user requests  

**Frontend**
- HTML, CSS, JavaScript (planned full-stack UI integration)

---

## 🏗️ System Architecture

1. **Frontend** → User defines AOIs & monitoring schedule.  
2. **Node.js API** → Stores requests in `monitoring_tasks.json`.  
3. **Python Scheduler** (`monitoring_scheduler.py`) → Reads tasks & triggers analysis.  
4. **Analysis Modules**
   - `cva_change_detection.py` → Change Vector Analysis  
   - `unet_inference.py` → Deep learning model inference  
5. **Output & Alerts** → Change masks & metadata generated, alerts sent if thresholds are exceeded.

---

## ⚙️ Setup and Installation

### Prerequisites
- Python **3.9+**
- Node.js & npm

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/rajkrsingh9/Gagan-Dhristi.git
   cd Gagan-Dhristi


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
