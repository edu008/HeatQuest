import React from 'react';

type Props = { children: React.ReactNode };

export class ErrorBoundary extends React.Component<Props, { hasError: boolean; error?: Error; info?: any }> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: any) {
    console.error('Global ErrorBoundary caught:', error, info);
    this.setState({ info });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 16,
          background: 'hsl(var(--background))',
          color: 'hsl(var(--foreground))',
        }}>
          <div style={{ maxWidth: 800 }}>
            <h1 style={{ fontSize: 24, fontWeight: 700 }}>Es ist ein Fehler aufgetreten</h1>
            <p style={{ opacity: 0.8, marginTop: 8 }}>Bitte lade die Seite neu. Wenn das Problem bleibt, schicke mir die Fehlermeldung unten.</p>
            {this.state.error && (
              <pre style={{
                marginTop: 16,
                padding: 12,
                border: '1px solid hsl(var(--border))',
                borderRadius: 12,
                overflow: 'auto',
                background: 'hsl(var(--card))',
                color: 'hsl(var(--card-foreground))',
                maxHeight: 300,
              }}>
                {this.state.error?.message}\n\n{this.state.error?.stack}
              </pre>
            )}
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
