import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WindwardPage } from '../features/overview/WindwardPage'
import { ErrorBoundary } from '../components/ErrorBoundary'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ErrorBoundary>
          <WindwardPage />
        </ErrorBoundary>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
