'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { date: 'Mon', likes: 45, comments: 12, shares: 8 },
  { date: 'Tue', likes: 52, comments: 15, shares: 10 },
  { date: 'Wed', likes: 38, comments: 8, shares: 5 },
  { date: 'Thu', likes: 65, comments: 20, shares: 15 },
  { date: 'Fri', likes: 72, comments: 25, shares: 18 },
  { date: 'Sat', likes: 55, comments: 14, shares: 12 },
  { date: 'Sun', likes: 48, comments: 11, shares: 9 },
]

export default function EngagementChart() {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Trends</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="likes"
              stroke="#0077B5"
              strokeWidth={2}
              dot={{ fill: '#0077B5' }}
            />
            <Line
              type="monotone"
              dataKey="comments"
              stroke="#00A0DC"
              strokeWidth={2}
              dot={{ fill: '#00A0DC' }}
            />
            <Line
              type="monotone"
              dataKey="shares"
              stroke="#86CFDA"
              strokeWidth={2}
              dot={{ fill: '#86CFDA' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-primary mr-2"></div>
          <span className="text-sm text-gray-600">Likes</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-secondary mr-2"></div>
          <span className="text-sm text-gray-600">Comments</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-[#86CFDA] mr-2"></div>
          <span className="text-sm text-gray-600">Shares</span>
        </div>
      </div>
    </div>
  )
}
