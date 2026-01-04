interface Post {
  id: string
  content: string
  status: 'published' | 'scheduled' | 'draft'
  engagement: { likes: number; comments: number }
  scheduledFor?: string
}

const posts: Post[] = [
  {
    id: '1',
    content: 'Exciting developments in AI safety research...',
    status: 'published',
    engagement: { likes: 45, comments: 12 },
  },
  {
    id: '2',
    content: 'The future of multimodal AI models...',
    status: 'scheduled',
    engagement: { likes: 0, comments: 0 },
    scheduledFor: '2026-01-04 09:00',
  },
  {
    id: '3',
    content: 'Breaking: New open-source LLM released...',
    status: 'draft',
    engagement: { likes: 0, comments: 0 },
  },
]

const statusStyles = {
  published: 'bg-green-100 text-green-800',
  scheduled: 'bg-blue-100 text-blue-800',
  draft: 'bg-gray-100 text-gray-800',
}

export default function RecentPosts() {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Posts</h3>
        <a href="/posts" className="text-sm text-primary hover:underline">
          View all
        </a>
      </div>

      <div className="space-y-4">
        {posts.map((post) => (
          <div key={post.id} className="border-b border-gray-100 pb-4 last:border-0">
            <div className="flex justify-between items-start">
              <p className="text-sm text-gray-700 line-clamp-2 flex-1">
                {post.content}
              </p>
              <span className={`ml-2 px-2 py-1 text-xs rounded-full ${statusStyles[post.status]}`}>
                {post.status}
              </span>
            </div>

            {post.status === 'published' && (
              <div className="flex gap-4 mt-2 text-xs text-gray-500">
                <span>{post.engagement.likes} likes</span>
                <span>{post.engagement.comments} comments</span>
              </div>
            )}

            {post.status === 'scheduled' && post.scheduledFor && (
              <p className="mt-2 text-xs text-gray-500">
                Scheduled for {post.scheduledFor}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
