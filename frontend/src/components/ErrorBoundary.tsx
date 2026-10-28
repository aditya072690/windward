import React from 'react'

type Props = { children: React.ReactNode; fallback?: React.ReactNode }

type State = { hasError: boolean; error?: Error; errorInfo?: React.ErrorInfo }

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error)
    console.error('Error stack:', error?.stack)
    console.error('Component stack:', errorInfo?.componentStack)
    this.setState({ errorInfo })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }
      const isDev = import.meta.env.DEV
      return (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-2)' }}>
          <p style={{ color: 'crimson', marginBottom: 8 }}>Something went wrong.</p>
          {this.state.error?.message && <p style={{ fontSize: 12, marginBottom: 8 }}>{this.state.error.message}</p>}
          {isDev && this.state.error?.stack && (
            <pre style={{ textAlign: 'left', overflow: 'auto', fontSize: 11, maxHeight: 200, background: '#f5f5f5', padding: 10 }}>
              {this.state.error.stack}
              {'\n\n'}
              {this.state.errorInfo?.componentStack}
            </pre>
          )}
          <button className="btn btn-ghost btn-compact" onClick={() => this.setState({ hasError: false, error: undefined, errorInfo: undefined })}>Try again</button>
        </div>
      )
    }
    return this.props.children
  }
}
