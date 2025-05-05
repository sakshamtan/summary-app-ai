'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { generateSummary, generateBulletPoints, logout } from '@/lib/api';
import toast from 'react-hot-toast';

export default function Home() {
  const router = useRouter();
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');
  const [bulletPoints, setBulletPoints] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      toast.error('Failed to logout');
    }
  };

  const handleGenerateSummary = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text first');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateSummary(text);
      setSummary(response.summary);
    } catch (error) {
      toast.error('Failed to generate summary');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateBulletPoints = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text first');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateBulletPoints(text);
      setBulletPoints(response.bullet_points);
    } catch (error) {
      toast.error('Failed to generate bullet points');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Text Summarizer</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Logout
          </button>
        </div>

        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <textarea
            className="w-full h-48 p-4 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Enter your text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="mt-4 flex space-x-4">
            <button
              onClick={handleGenerateSummary}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? 'Generating...' : 'Generate Summary'}
            </button>
            <button
              onClick={handleGenerateBulletPoints}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? 'Generating...' : 'Generate Bullet Points'}
            </button>
          </div>
        </div>

        {summary && (
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Summary</h2>
            <p className="text-gray-700">{summary}</p>
          </div>
        )}

        {bulletPoints.length > 0 && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Bullet Points</h2>
            <ul className="list-disc list-inside space-y-2">
              {bulletPoints.map((point, index) => (
                <li key={index} className="text-gray-700">
                  {point}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
