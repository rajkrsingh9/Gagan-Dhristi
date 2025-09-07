# Gagan Dhristi

## 🌍 Change Detection and Monitoring System

A robust, full-stack platform designed to **automatically detect and monitor changes on the Earth's surface** using multi-temporal satellite imagery.  
The system automates the process of comparing two satellite images of the same location, taken at different times, to identify significant changes such as **new construction, deforestation, or land-use shifts**.

---

## Glances of this masterpiece
### Change Detection
<img src="https://github.com/user-attachments/assets/18956ee9-c04f-4d82-8d2b-e5904732b6c4" height="400" alt="change detection">


<div align="center">
  <h2>Detection Algorithms and Robust Monitoring</h2>
  <img src="https://github.com/user-attachments/assets/383fa584-021b-4ce3-9a9d-98dd350f0246" width="25%" alt="change detection">
  <img src="https://github.com/user-attachments/assets/4730f251-802f-4c02-a579-bedbb77b5147" width="65%" alt="change detection">
 
</div>

### Downloadable Outputs
<img src="https://github.com/user-attachments/assets/c4a74116-73c1-4802-9a58-88e5c5425d22" height="400" alt="change detection">


## Outputs Files and Images(Mask)

<div align="center">
  <img src="https://github.com/user-attachments/assets/bcd44bd4-8968-41bb-ad6c-1f046b6d1fc8" alt="Image 1" width="45%">
  <img src="https://github.com/user-attachments/assets/3eef86ab-2e71-4d22-9cb1-e2c2f4c9903d" alt="Image 2" width="45%">
</div>
<img src="https://github.com/user-attachments/assets/00cee112-ac59-4ff2-9321-8701ef3652a0" alt="Image 3" width="98%">

### Email Alerts

<img width="837" height="501" alt="image" src="https://github.com/user-attachments/assets/e2c3b58d-4473-4cf7-b11d-a9c901c5498e" />



## 🏆 Achievements

This project advanced to the **Finals of ISRO BAH 2025** 🚀,  
representing our team **The Cache Crew**.

**Team Members:**
- [Rashmita Debnath](https://github.com/Rashmita-17)
- [Amol Chaurasia](https://github.com/Amol-Cld)
- [Aharshi Lodh](https://github.com/Aharshi-44)

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
