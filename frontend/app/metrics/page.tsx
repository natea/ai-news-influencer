'use client'

import { useState, useEffect } from 'react'

interface Metrics {
  total_tweets: number
  total_posts: number
  total_engagement: number
  avg_likes: number
  avg_comments: number
  engagement_rate: number
}

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchMetrics() {
      try {
        const res = await fetch('/api/v1/metrics')
        if (res.ok) {
          const data = await res.json()
          setMetrics(data)
        }
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchMetrics()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading metrics...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Metrics</h1>
        <p className="text-gray-600">Analytics and performance tracking</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="text-sm text-gray-500 mb-1">Total Tweets Scraped</div>
          <div className="text-3xl font-bold text-gray-900">{metrics?.total_tweets || 0}</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="text-sm text-gray-500 mb-1">Posts Generated</div>
          <div className="text-3xl font-bold text-gray-900">{metrics?.total_posts || 0}</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="text-sm text-gray-500 mb-1">Total Engagement</div>
          <div className="text-3xl font-bold text-gray-900">{metrics?.total_engagement || 0}</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="text-sm text-gray-500 mb-1">Avg. Likes per Post</div>
          <div className="text-3xl font-bold text-primary">{metrics?.avg_likes?.toFixed(1) || 0}</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="text-sm text-gray-500 mb-1">Avg. Comments per Post</div>
          <div className="text-3xl font-bold text-primary">{metrics?.avg_comments?.toFixed(1) || 0}</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="text-sm text-gray-500 mb-1">Engagement Rate</div>
          <div className="text-3xl font-bold text-green-600">
            {((metrics?.engagement_rate || 0) * 100).toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Insights</h2>
        <div className="text-gray-500 text-center py-8">
          <div className="text-4xl mb-4">📊</div>
          <p>Generate and publish posts to see detailed analytics</p>
        </div>
      </div>
    </div>
  )
}
