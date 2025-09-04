import Link from 'next/link'
import type { ReactNode } from 'react'
import '../globals.css'

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen grid grid-rows-[auto,1fr]">
      <header className="border-b">
        <div className="mx-auto max-w-6xl p-4 flex items-center gap-6">
          <h1 className="font-semibold">NL Highschools</h1>
          <nav className="text-sm text-slate-600 flex gap-4">
            <Link href="/dashboard">Overview</Link>
            <Link href="/map">Map</Link>
            <Link href="/schools">Schools</Link>
          </nav>
          <div className="ml-auto">
            <Link className="text-sm text-blue-600" href="/auth/sign-in">Sign in</Link>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl w-full p-6">{children}</main>
    </div>
  )
}

