'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Force dynamic rendering to prevent SSR issues
export const dynamic = 'force-dynamic';

export default function Page() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        router.push('/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
    </div>
  );
}
