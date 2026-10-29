import { useQuery } from '@tanstack/react-query'
import { fetchMeta } from './api'

export type Meta = {
  timezone?: string
  decision_window?: [string, string]
  delivery_day_min?: string
  delivery_day_max?: string
  period_start?: string
  period_end_exclusive?: string
  data_as_of?: string
  counts?: { actual_wind?: number | null; wind_forecast?: number | null }
  source?: string
  cache?: any
  status?: string
  done?: number
  total?: number
}

export function useMeta() {
  const query = useQuery({
    queryKey: ['meta'],
    queryFn: fetchMeta,
    refetchInterval: (data: any) => {
      if (data?.state?.data?.status === 'warming' || data?.status === 'warming') {
        return 3000
      }
      const res = data as any
      if (res && res.status === 'warming') return 3000
      return false
    },
    staleTime: Infinity,
  })

  const data: any = query.data
  const isWarming = data?.status === 'warming'
  const isStale = data?.stale === true

  return {
    meta: data as Meta | undefined,
    isLoading: query.isLoading,
    isWarming,
    isError: query.isError,
    error: query.error,
    isStale,
    refetch: query.refetch,
  }
}
