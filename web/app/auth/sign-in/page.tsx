"use client";
import { useState } from 'react'
import { getBrowserSupabase } from '@/lib/supabase/client'

export default function SignInPage() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus(null)
    setError(null)
    try {
      const supabase = getBrowserSupabase()
      const redirectTo = `${window.location.origin}/auth/callback?next=/dashboard`
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: { emailRedirectTo: redirectTo, shouldCreateUser: false },
      })
      if (error) throw error
      setStatus('Check your email for a magic link to sign in.')
    } catch (err: any) {
      setError(err?.message || 'Sign-in failed')
    }
  }

  return (
    <div className="max-w-sm mx-auto space-y-4">
      <h2 className="text-xl font-semibold">Sign in</h2>
      <p className="text-sm text-slate-600">Enter your email; we will send you a magic link.</p>
      <form onSubmit={onSubmit} className="space-y-3">
        <div>
          <label htmlFor="email" className="block text-xs text-slate-600 mb-1">Email</label>
          <input id="email" type="email" required className="w-full border rounded px-3 py-2" value={email} onChange={(e)=>setEmail(e.target.value)} />
        </div>
        <button type="submit" className="border rounded px-3 py-2 text-sm">Send magic link</button>
      </form>
      {status && <div className="text-sm text-green-700">{status}</div>}
      {error && <div className="text-sm text-red-700">{error}</div>}
    </div>
  )
}

