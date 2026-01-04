'use client'

import { useState, useEffect } from 'react'

interface Post {
  id: string
  content: string
  status: string
  created_at: string
  likes?: number
  comments?: number
  shares?: number
}

export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchPosts() {
      try {
        const res = await fetch('/api/v1/posts')
        if (res.ok) {
          const data = await res.json()
          setPosts(data.posts || [])
        }
      } catch (error) {
        console.error('Failed to fetch posts:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchPosts()
  }, [])

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      pending_approval: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-blue-100 text-blue-800',
      published: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading posts...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Posts</h1>
          <p className="text-gray-600">Manage generated LinkedIn posts</p>
        </div>
        <button className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">
          + Generate New Post
        </button>
      </header>

      {posts.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="text-4xl mb-4">📝</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No posts yet</h3>
          <p className="text-gray-500 mb-4">
            Scrape tweets and generate LinkedIn posts to see them here.
          </p>
          <p className="text-sm text-gray-400">
            Use the CLI: <code className="bg-gray-100 px-2 py-1 rounded">python -m src.cli scrape --accounts "@OpenAI" --demo</code>
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {posts.map((post) => (
            <div
              key={post.id}
              className="bg-white rounded-lg border border-gray-200 p-6"
            >
              <div className="flex justify-between items-start mb-4">
                <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusBadge(post.status)}`}>
                  {post.status.replace('_', ' ').toUpperCase()}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(post.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-gray-700 whitespace-pre-wrap">{post.content}</p>
              {post.status === 'published' && (
                <div className="mt-4 pt-4 border-t border-gray-100 flex gap-6 text-sm text-gray-500">
                  <span>❤️ {post.likes || 0}</span>
                  <span>💬 {post.comments || 0}</span>
                  <span>🔄 {post.shares || 0}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
