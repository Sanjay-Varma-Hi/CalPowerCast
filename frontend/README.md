# CalPowerCast Frontend

A modern Next.js frontend for visualizing electricity consumption forecasts for California counties.

## Features

- 🎯 Select from 14 major California counties
- 📊 Interactive line chart showing monthly forecasts
- 📥 Download forecast data as CSV
- 📱 Fully responsive design
- ⚡ Real-time loading states
- 🚨 Error handling and empty states
- 🎨 Beautiful Tailwind CSS styling

## Getting Started

### Install Dependencies

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Composable charting library

## API Endpoint

The frontend connects to the Hugging Face API:
```
https://sanjayvarma123-calpowercast.hf.space/forecast?county={COUNTY_NAME}
```

## Deployment

### Deploy to Vercel

1. Push your code to GitHub
2. Import the project on [Vercel](https://vercel.com)
3. Vercel will automatically detect Next.js and deploy

### Manual Deployment

```bash
npm run build
# Deploy the .next folder to your hosting service
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main page component
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```
