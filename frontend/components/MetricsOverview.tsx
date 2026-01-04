interface MetricCardProps {
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
}

function MetricCard({ title, value, change, changeType = 'neutral' }: MetricCardProps) {
  const changeColors = {
    positive: 'text-green-600',
    negative: 'text-red-600',
    neutral: 'text-gray-600',
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <div className="mt-2 flex items-baseline">
        <p className="text-3xl font-semibold text-gray-900">{value}</p>
        {change && (
          <span className={`ml-2 text-sm ${changeColors[changeType]}`}>
            {change}
          </span>
        )}
      </div>
    </div>
  )
}

export default function MetricsOverview() {
  // In real app, this would fetch from API
  const metrics = {
    totalPosts: 47,
    avgEngagement: '4.2%',
    responseRate: '87%',
    impressions: '12.4K',
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="Total Posts"
        value={metrics.totalPosts}
        change="+5 this week"
        changeType="positive"
      />
      <MetricCard
        title="Avg Engagement"
        value={metrics.avgEngagement}
        change="+0.8%"
        changeType="positive"
      />
      <MetricCard
        title="Response Rate"
        value={metrics.responseRate}
        change="-2%"
        changeType="negative"
      />
      <MetricCard
        title="Impressions"
        value={metrics.impressions}
        change="+1.2K"
        changeType="positive"
      />
    </div>
  )
}
