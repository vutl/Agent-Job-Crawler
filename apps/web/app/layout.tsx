import './globals.css';
import React from 'react';

export const metadata = {
  title: 'AI Job Intelligence Platform',
  description: 'Real-time tech skill analytics and AI job market intelligence dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0b0f19] text-gray-100 min-h-screen flex flex-col">
        <header className="border-b border-gray-800 bg-[#111827]/80 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-400 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
                AI
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-400">
                AI Job Intelligence
              </span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-gray-400">
              <span className="hover:text-white transition cursor-pointer">Overview</span>
              <span className="hover:text-white transition cursor-pointer">Role Analytics</span>
              <span className="hover:text-white transition cursor-pointer">Roadmaps</span>
              <div className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>System Active</span>
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-800 py-6 text-center text-sm text-gray-500">
          AI Job Intelligence Platform • Powered by FastAPI, PostgreSQL, Redis, LangChain & 9Router
        </footer>
      </body>
    </html>
  );
}
