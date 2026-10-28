import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WindwardPage } from '../features/overview/WindwardPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WindwardPage />
    </QueryClientProvider>
  )
}

export default App
