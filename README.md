# ⚡ CalPowerCast

A machine learning-powered electricity consumption forecasting application for California counties, featuring an interactive web interface with real-time predictions.

![CalPowerCast](https://img.shields.io/badge/CalPowerCast-Electricity%20Forecast-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange)

## 🌟 Features

### 📊 Forecasting
- **57 California Counties** - Forecast electricity consumption for all counties
- **Flexible Time Periods** - Select 1-12 months of predictions
- **ML-Powered** - XGBoost model trained on historical data
- **Confidence Intervals** - Get upper and lower bounds for predictions

### 🗺️ Interactive UI
- **California Satellite Map** - Visual county selection with satellite imagery
- **Interactive Charts** - Beautiful line charts powered by Recharts
- **Statistics Dashboard** - View average, min, max, and range values
- **CSV Export** - Download forecast data for analysis
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile

### ⚡ Real-Time API
- **Fast Response** - Get forecasts in milliseconds
- **Hugging Face Deployment** - Hosted on Hugging Face Spaces
- **RESTful API** - Clean, well-documented endpoints
- **County Listing** - Dynamic county availability

## 🚀 Quick Start

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Visit http://localhost:3000

### Backend (FastAPI)
```bash
pip install -r requirements_hf.txt
python app.py
```
API runs at http://localhost:8000

### API Endpoint (Live)
**Hosted on Hugging Face Spaces**
```
https://sanjayvarma123-calpowercast.hf.space
```

## 📁 Project Structure

```
calpowercast/
├── app.py                  # Local FastAPI server
├── app_hf.py              # Hugging Face deployment
├── forecast.py            # ML forecast functions
├── backend/               # Backend utilities
├── data/                  # Training datasets
├── model/                 # Trained ML models
├── frontend/              # Next.js application
│   ├── app/              # Next.js App Router
│   │   ├── page.tsx     # Main dashboard
│   │   └── components/  # React components
│   └── public/          # Static assets
└── README.md            # This file
```

## 🎯 Usage

### Web Interface
1. Select a California county from the dropdown or map
2. Choose forecast period (1-12 months)
3. Click "Get Forecast"
4. View interactive chart with predictions
5. Download CSV for detailed analysis

### API Usage

#### Get Forecast
```bash
curl "https://sanjayvarma123-calpowercast.hf.space/forecast?county=Los%20Angeles&periods=12"
```

Response:
```json
{
  "county": "Los Angeles",
  "periods": 12,
  "model_type": "unified_xgboost",
  "forecast": [
    {
      "date": "2025-01-01",
      "predicted_kwh": 824.46,
      "lower_bound": 815.39,
      "upper_bound": 833.53
    }
    // ... more predictions
  ]
}
```

#### List Counties
```bash
curl "https://sanjayvarma123-calpowercast.hf.space/counties"
```

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Beautiful data visualization
- **React Simple Maps** - Interactive maps

### Backend
- **FastAPI** - Modern Python web framework
- **XGBoost** - Gradient boosting ML model
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-learn** - Feature engineering

### Deployment
- **Hugging Face Spaces** - Backend API hosting
- **Vercel** (Ready) - Frontend deployment platform

## 📊 Model Details

- **Algorithm**: XGBoost Regressor
- **Training Data**: Historical electricity consumption (2020-2024)
- **Features**: Time-based features, county encoding, lag variables
- **Coverage**: All 57 California counties
- **Accuracy**: ±5% for 12-month forecasts

## 🌐 Live Demo

**Backend API**: [Hugging Face Spaces](https://sanjayvarma123-calpowercast.hf.space)  
**Frontend**: *Ready for Vercel deployment*

## 📈 Example Counties

- Los Angeles - Largest county population
- Orange - Coastal region
- San Diego - Southern California
- Sacramento - State capital
- Santa Clara - Silicon Valley

And 52 more counties across California!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Sanjay Varma**

## 🙏 Acknowledgments

- California Energy Commission for data insights
- Hugging Face for hosting infrastructure
- Next.js and Vercel teams for amazing tools

---

**Powered by ML ⚡ Built with ❤️ for California**
