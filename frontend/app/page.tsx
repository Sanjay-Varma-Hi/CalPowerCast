'use client'

import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import CaliforniaMap from './components/CaliforniaMap'

interface ForecastData {
  ds: string
  yhat: number
}

interface ForecastItem {
  date: string
  predicted_kwh: number
  lower_bound?: number
  upper_bound?: number
}

const API_BASE_URL = 'https://sanjayvarma123-calpowercast.hf.space'

interface CountiesResponse {
  total_counties: number
  counties: string[]
}

export default function Home() {
  const [counties, setCounties] = useState<string[]>(['Santa Clara'])
  const [county, setCounty] = useState('Santa Clara')
  const [months, setMonths] = useState(12)
  const [forecastData, setForecastData] = useState<ForecastData[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingCounties, setLoadingCounties] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch available counties on component mount
  useEffect(() => {
    const fetchCounties = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/counties`)
        if (!response.ok) {
          throw new Error('Failed to fetch counties')
        }
        const data: CountiesResponse = await response.json()
        setCounties(data.counties)
        // Set initial county to Santa Clara or first one in list
        if (data.counties.length > 0 && !data.counties.includes('Santa Clara')) {
          setCounty(data.counties[0])
        }
      } catch (err) {
        console.error('Error fetching counties:', err)
        // Keep the default county list if API fails
      } finally {
        setLoadingCounties(false)
      }
    }
    fetchCounties()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchForecast = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const encodedCounty = encodeURIComponent(county)
      const response = await fetch(
        `${API_BASE_URL}/forecast?county=${encodedCounty}&periods=${months}`
      )
      
      if (!response.ok) {
        throw new Error(`Failed to fetch forecast: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      // Handle different response formats
      let forecast: ForecastItem[] = []
      
      // Check if response has a 'forecast' property (new format)
      if (data && data.forecast && Array.isArray(data.forecast)) {
        forecast = data.forecast
      } 
      // Check if response is directly an array (old format)
      else if (Array.isArray(data)) {
        // Map old format to new format
        forecast = data.map(item => ({
          date: item.ds || item.date,
          predicted_kwh: item.yhat || item.predicted_kwh,
          lower_bound: item.lower_bound,
          upper_bound: item.upper_bound
        }))
      } else {
        throw new Error('Invalid response format from API')
      }
      
      // Check if data is empty
      if (forecast.length === 0) {
        throw new Error('No forecast data available for this county')
      }
      
      // Validate data structure
      const isValidData = forecast.every(item => 
        item && typeof item.date === 'string' && typeof item.predicted_kwh === 'number'
      )
      
      if (!isValidData) {
        throw new Error('Invalid data structure in API response')
      }
      
      // Convert to format expected by chart component
      const formattedData: ForecastData[] = forecast.map(item => ({
        ds: item.date,
        yhat: item.predicted_kwh
      }))
      
      setForecastData(formattedData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setForecastData([])
    } finally {
      setLoading(false)
    }
  }

  const downloadCSV = () => {
    if (forecastData.length === 0) return

    const headers = ['Date', 'Forecasted Consumption (kWh)']
    const csvContent = [
      headers.join(','),
      ...forecastData.map(item => 
        `${item.ds},${item.yhat}`
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `calpowercast_${county.replace(/\s+/g, '_')}_forecast.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const getForecastYearRange = () => {
    if (forecastData.length === 0) return null
    const dates = forecastData.map(d => new Date(d.ds))
    const minDate = new Date(Math.min(...dates.map(d => d.getTime())))
    const maxDate = new Date(Math.max(...dates.map(d => d.getTime())))
    const minYear = minDate.getFullYear()
    const maxYear = maxDate.getFullYear()
    if (minYear === maxYear) {
      return minYear.toString()
    }
    return `${minYear} - ${maxYear}`
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            CalPowerCast ⚡
          </h1>
          <p className="text-xl text-gray-600">
            Forecast electricity consumption for California counties
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 mb-8">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1">
              <label htmlFor="county-select" className="block text-sm font-medium text-gray-700 mb-2">
                Select County {loadingCounties && '(loading...)'}
              </label>
              <select
                id="county-select"
                value={county}
                onChange={(e) => setCounty(e.target.value)}
                disabled={loadingCounties}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                {counties.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="w-full sm:w-48">
              <label htmlFor="months-select" className="block text-sm font-medium text-gray-700 mb-2">
                Forecast Period
              </label>
              <select
                id="months-select"
                value={months}
                onChange={(e) => setMonths(Number(e.target.value))}
                disabled={loadingCounties}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                {Array.from({ length: 12 }, (_, i) => i + 1).map((num) => (
                  <option key={num} value={num}>
                    {num} {num === 1 ? 'Month' : 'Months'}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={fetchForecast}
              disabled={loading || loadingCounties}
              className="w-full sm:w-auto px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Fetching...
                </span>
              ) : (
                'Get Forecast'
              )}
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-lg font-semibold text-red-900">Error</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Chart Section */}
        {forecastData.length > 0 && (
          <div className="mb-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Side: Map */}
              <div className="lg:col-span-1">
                <CaliforniaMap
                  counties={counties}
                  selectedCounty={county}
                  onCountySelect={setCounty}
                />
              </div>

              {/* Right Side: Chart */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 h-full">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                    <div>
                      <h2 className="text-3xl font-bold text-gray-900 mb-2">
                        {county} County Forecast
                      </h2>
                      <p className="text-gray-600">
                        {forecastData.length} months of predicted electricity consumption
                        {getForecastYearRange() && (
                          <span className="ml-2 text-indigo-600 font-semibold">
                            (Year: {getForecastYearRange()})
                          </span>
                        )}
                      </p>
                    </div>
                    <button
                      onClick={downloadCSV}
                      className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors flex items-center gap-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download CSV
                    </button>
                  </div>

                  <ResponsiveContainer width="100%" height={500}>
                    <LineChart data={forecastData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis 
                        dataKey="ds" 
                        tickFormatter={formatDate}
                        stroke="#6b7280"
                        style={{ fontSize: '12px' }}
                      />
                      <YAxis 
                        stroke="#6b7280"
                        style={{ fontSize: '12px' }}
                        label={{ value: 'kWh', angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip 
                        formatter={(value: number) => [`${value.toFixed(2)} kWh`, 'Forecast']}
                        labelFormatter={(label) => formatDate(label)}
                        contentStyle={{ 
                          backgroundColor: 'white', 
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          padding: '12px'
                        }}
                      />
                      <Legend wrapperStyle={{ paddingTop: '20px' }} />
                      <Line 
                        type="monotone" 
                        dataKey="yhat" 
                        stroke="#2563eb" 
                        strokeWidth={3}
                        dot={{ fill: '#2563eb', r: 4 }}
                        activeDot={{ r: 6 }}
                        name="Predicted Consumption"
                      />
                    </LineChart>
                  </ResponsiveContainer>

                  {/* Stats Summary */}
                  <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-600 mb-1">Average</p>
                      <p className="text-2xl font-bold text-blue-700">
                        {(forecastData.reduce((sum, d) => sum + d.yhat, 0) / forecastData.length).toFixed(1)} kWh
                      </p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-600 mb-1">Min</p>
                      <p className="text-2xl font-bold text-green-700">
                        {Math.min(...forecastData.map(d => d.yhat)).toFixed(1)} kWh
                      </p>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-600 mb-1">Max</p>
                      <p className="text-2xl font-bold text-orange-700">
                        {Math.max(...forecastData.map(d => d.yhat)).toFixed(1)} kWh
                      </p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-600 mb-1">Range</p>
                      <p className="text-2xl font-bold text-purple-700">
                        {(Math.max(...forecastData.map(d => d.yhat)) - Math.min(...forecastData.map(d => d.yhat))).toFixed(1)} kWh
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && forecastData.length === 0 && !error && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <svg className="w-24 h-24 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-2xl font-semibold text-gray-900 mb-2">
              No Data Yet
            </h3>
            <p className="text-gray-600">
              Select a county and click "Get Forecast" to see the prediction
            </p>
          </div>
        )}
      </div>
    </main>
  )
}
