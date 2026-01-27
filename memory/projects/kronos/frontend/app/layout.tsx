import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Sidebar } from '@/components/layout/Sidebar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Kronos - Tax Practice Management',
  description: 'Modern tax practice management platform for CPAs and tax professionals',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="flex min-h-screen bg-gray-50">
            {/* Sidebar */}
            <Sidebar />
            
            {/* Main content */}
            <main className="flex-1 ml-64 p-8">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  )
}