import MetricsOverview from '@/components/MetricsOverview'
import RecentPosts from '@/components/RecentPosts'
import EngagementChart from '@/components/EngagementChart'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">AI News Influencer Overview</p>
      </header>

      <MetricsOverview />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EngagementChart />
        <RecentPosts />
      </div>
    </div>
  )
}
