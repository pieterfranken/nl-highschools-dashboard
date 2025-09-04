import { NextResponse, NextRequest } from 'next/server'
import { createMiddlewareClient } from '@supabase/ssr'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })
  const {
    data: { session },
  } = await supabase.auth.getSession()

  const isAuthRoute = req.nextUrl.pathname.startsWith('/auth')
  const isPublicRoute = ['/', '/map'].includes(req.nextUrl.pathname)

  if (!session && !isAuthRoute && !isPublicRoute) {
    const url = req.nextUrl.clone()
    url.pathname = '/auth/sign-in'
    url.searchParams.set('next', req.nextUrl.pathname)
    return NextResponse.redirect(url)
  }

  return res
}

export const config = {
  matcher: ['/((?!_next|api|favicon.ico|.*\\.(?:png|jpg|svg)).*)'],
}

