import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  // We need a mutable response so the Supabase SSR helper can
  // refresh the session cookie transparently on every request.
  let response = NextResponse.next({
    request: { headers: request.headers },
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          // Forward updated cookies to both the outgoing request and response
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // Refresh the session (keeps short-lived tokens alive)
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { pathname } = request.nextUrl;

  // ── Unauthenticated visitors ──────────────────────────────────
  if (!user) {
    if (pathname.startsWith('/admin')) {
      return NextResponse.redirect(new URL('/admin/login', request.url));
    }
    if (pathname.startsWith('/student')) {
      return NextResponse.redirect(new URL('/student/login', request.url));
    }
    return response;
  }

  // ── Authenticated visitors trying to reach /admin/* ──────────
  if (pathname.startsWith('/admin')) {
    // Skip the login page itself so we don't create a redirect loop
    if (pathname === '/admin/login') {
      return response;
    }

    // Query the profiles table to verify the admin role
    const { data: profile, error } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single();

    if (error || !profile || profile.role !== 'admin') {
      // Not an admin → bounce to student dashboard
      return NextResponse.redirect(new URL('/student/dashboard', request.url));
    }
  }

  // ── Authenticated admin/student visiting their own login page ─
  // (optional UX: skip login if already signed in)
  if (user && pathname === '/student/login') {
    return NextResponse.redirect(new URL('/student/dashboard', request.url));
  }
  if (user && pathname === '/admin/login') {
    // Only redirect admins away from admin/login; students land on /student/dashboard
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single();

    if (profile?.role === 'admin') {
      return NextResponse.redirect(new URL('/admin/dashboard', request.url));
    }
    return NextResponse.redirect(new URL('/student/dashboard', request.url));
  }

  return response;
}

// Only run this middleware on protected route segments
export const config = {
  matcher: ['/student/:path*', '/admin/:path*'],
};
