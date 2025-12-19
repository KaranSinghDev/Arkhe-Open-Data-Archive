export function CardSkeleton() {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 space-y-3 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-100 rounded w-full" />
      <div className="h-3 bg-gray-100 rounded w-2/3" />
      <div className="flex gap-2 mt-2">
        <div className="h-5 w-16 bg-gray-100 rounded" />
        <div className="h-5 w-12 bg-gray-100 rounded" />
      </div>
    </div>
  )
}

export function SkeletonList({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => <CardSkeleton key={i} />)}
    </div>
  )
}
