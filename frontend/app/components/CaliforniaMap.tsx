'use client'

interface CaliforniaMapProps {
  counties: string[]
  selectedCounty: string
  onCountySelect: (county: string) => void
}

export default function CaliforniaMap({ counties, selectedCounty, onCountySelect }: CaliforniaMapProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 h-full flex flex-col">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Select County</h3>
      
      {/* California Satellite Map Image */}
      <div className="border-2 border-gray-200 rounded-lg bg-gray-50 flex-1 flex items-center justify-center mb-4 overflow-hidden min-h-[400px] max-h-[500px]">
        <img
          src="/California-Satellite-County-Map.jpg"
          alt="California County Map"
          className="w-full h-full object-contain"
          style={{ maxWidth: '100%', maxHeight: '100%' }}
          onError={(e) => {
            e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><text x="50%25" y="50%25" text-anchor="middle" fill="%23666" font-size="16">California Map Image</text></svg>'
          }}
        />
      </div>

      {/* Selected County Display */}
      <div className="border-t pt-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-gray-700">Selected:</p>
          <span className="px-3 py-1 bg-blue-600 text-white text-sm font-semibold rounded-lg">
            {selectedCounty}
          </span>
        </div>
        
        {/* County selector */}
        <details className="cursor-pointer">
          <summary className="text-sm text-gray-600 font-medium mb-2">
            Browse all 57 counties
          </summary>
          <div className="grid grid-cols-3 gap-2 max-h-[150px] overflow-y-auto mt-2">
            {counties.map((county) => (
              <button
                key={county}
                onClick={() => onCountySelect(county)}
                className={`px-2 py-1.5 text-xs rounded-md transition-colors text-left ${
                  selectedCounty === county
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                title={county}
              >
                {county.length > 10 ? county.substring(0, 10) + '...' : county}
              </button>
            ))}
          </div>
        </details>
      </div>
    </div>
  )
}
