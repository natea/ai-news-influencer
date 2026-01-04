'use client'

import { useState } from 'react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    autoPublish: false,
    maxPostsPerDay: 3,
    preferredStyle: 'informative',
    targetAccounts: '@OpenAI, @AnthropicAI',
  })

  const handleSave = () => {
    // TODO: Save settings to backend
    alert('Settings saved (demo mode)')
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Configure your AI News Influencer</p>
      </header>

      <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
        {/* Auto Publish */}
        <div className="p-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Auto Publish</h3>
              <p className="text-sm text-gray-500">Automatically publish approved posts</p>
            </div>
            <button
              onClick={() => setSettings(s => ({ ...s, autoPublish: !s.autoPublish }))}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.autoPublish ? 'bg-primary' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.autoPublish ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Max Posts Per Day */}
        <div className="p-6">
          <label className="block">
            <span className="text-sm font-medium text-gray-900">Max Posts Per Day</span>
            <p className="text-sm text-gray-500 mb-2">Limit daily post generation</p>
            <input
              type="number"
              min="1"
              max="10"
              value={settings.maxPostsPerDay}
              onChange={(e) => setSettings(s => ({ ...s, maxPostsPerDay: parseInt(e.target.value) }))}
              className="mt-1 block w-32 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
            />
          </label>
        </div>

        {/* Preferred Style */}
        <div className="p-6">
          <label className="block">
            <span className="text-sm font-medium text-gray-900">Default Post Style</span>
            <p className="text-sm text-gray-500 mb-2">Style for generated LinkedIn posts</p>
            <select
              value={settings.preferredStyle}
              onChange={(e) => setSettings(s => ({ ...s, preferredStyle: e.target.value }))}
              className="mt-1 block w-64 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
            >
              <option value="informative">Informative</option>
              <option value="thought_leadership">Thought Leadership</option>
              <option value="commentary">Commentary</option>
            </select>
          </label>
        </div>

        {/* Target Accounts */}
        <div className="p-6">
          <label className="block">
            <span className="text-sm font-medium text-gray-900">Target Twitter Accounts</span>
            <p className="text-sm text-gray-500 mb-2">Accounts to scrape (comma-separated)</p>
            <input
              type="text"
              value={settings.targetAccounts}
              onChange={(e) => setSettings(s => ({ ...s, targetAccounts: e.target.value }))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
              placeholder="@OpenAI, @AnthropicAI, @GoogleAI"
            />
          </label>
        </div>
      </div>

      {/* API Keys Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">API Configuration</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <span className="font-medium text-gray-900">Anthropic API</span>
              <p className="text-sm text-gray-500">Claude for content generation</p>
            </div>
            <span className="px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800">Configured</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <span className="font-medium text-gray-900">LinkedIn OAuth</span>
              <p className="text-sm text-gray-500">For publishing posts</p>
            </div>
            <span className="px-2 py-1 text-xs font-medium rounded bg-yellow-100 text-yellow-800">Not Configured</span>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
        >
          Save Settings
        </button>
      </div>
    </div>
  )
}
