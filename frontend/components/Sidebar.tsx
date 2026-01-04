'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/', icon: '📊' },
  { name: 'Posts', href: '/posts', icon: '📝' },
  { name: 'Metrics', href: '/metrics', icon: '📈' },
  { name: 'Settings', href: '/settings', icon: '⚙️' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <div className="p-6">
        <h2 className="text-xl font-bold text-primary">AI News Influencer</h2>
      </div>

      <nav className="px-4 space-y-1">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={clsx(
              'flex items-center px-4 py-3 text-sm font-medium rounded-lg',
              pathname === item.href
                ? 'bg-primary text-white'
                : 'text-gray-700 hover:bg-gray-100'
            )}
          >
            <span className="mr-3">{item.icon}</span>
            {item.name}
          </Link>
        ))}
      </nav>

      <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200">
        <div className="flex items-center">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          <span className="text-sm text-gray-600">System Active</span>
        </div>
      </div>
    </aside>
  )
}
