'use client';

import { useEffect, useState } from 'react';
import NDAModal from '@/components/NDAModal';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [ndaAccepted, setNdaAccepted] = useState<boolean | null>(null);

  useEffect(() => {
    // Check NDA acceptance status
    fetch('/api/user/nda-acceptance')
      .then((res) => res.json())
      .then((data) => setNdaAccepted(data.accepted))
      .catch(() => setNdaAccepted(false));
  }, []);

  if (ndaAccepted === null) {
    return (
      <html lang="en">
        <body>
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-gray-500">Loading...</div>
          </div>
        </body>
      </html>
    );
  }

  return (
    <html lang="en">
      <body>
        {!ndaAccepted && <NDAModal onAccept={() => setNdaAccepted(true)} />}
        {children}
      </body>
    </html>
  );
}
