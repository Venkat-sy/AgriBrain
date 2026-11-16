import React from "react";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] px-4 text-center">
      <h1 className="mb-4 text-6xl font-bold text-slate-900">404</h1>
      <p className="mb-6 text-lg text-slate-600">
        Sorry, the page you&apos;re looking for doesn&apos;t exist.
      </p>
      <Link
        href="/"
        className="rounded-md bg-slate-900 px-6 py-3 text-sm font-medium text-white hover:bg-slate-900/90"
      >
        Go back home
      </Link>
    </div>
  );
}

export const dynamic = "force-dynamic";