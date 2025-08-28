'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-gray-300">500</h1>
          <p className="text-xl text-gray-600 mt-2">Something went wrong!</p>
        </div>
        <p className="text-gray-500 mb-8">
          An error occurred while processing your request.
        </p>
        <div className="space-x-4">
          <button
            onClick={() => reset()}
            className="inline-block bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try again
          </button>
          <a
            href="/"
            className="inline-block bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-colors"
          >
            Go Home
          </a>
        </div>
      </div>
    </div>
  )
}
