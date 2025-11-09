import React from 'react';

type Props = { children: React.ReactNode };

type State = { hasError: boolean; error?: any };

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: any): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: any, errorInfo: any) {
    // Log visibly to the DOM for debugging when console is unavailable
    const el = document.getElementById('root');
    if (el) {
      const pre = document.createElement('pre');
      pre.style.padding = '16px';
      pre.style.whiteSpace = 'pre-wrap';
      pre.style.background = '#fee';
      pre.style.color = '#900';
      pre.textContent = `App crashed:\n${String(error)}\n\n${errorInfo?.componentStack ?? ''}`;
      el.appendChild(pre);
    }
    console.error('[ErrorBoundary]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24 }}>
          <h1>Etwas ist schief gelaufen.</h1>
          <p>{String(this.state.error || 'Unbekannter Fehler')}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
