import './globals.css'
import type { ReactNode } from 'react'

export const metadata = {
  title: 'NL Highschools Dashboard',
  description: 'Next.js + Supabase migration of Streamlit app',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-slate-900">
        {children}
      </body>
    </html>
  )
}

