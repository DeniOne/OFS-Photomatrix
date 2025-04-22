import { Component, ErrorInfo, ReactNode } from 'react';
import { Alert } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

interface Props {
  children: ReactNode;
  fallbackMessage?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Обновить состояние, чтобы следующий рендер показал запасной UI.
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Можно также логировать ошибку в сервис отчетов об ошибках
    console.error("ErrorBoundary поймал ошибку:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      // Можно отрендерить любой запасной UI
      return (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка компонента!" color="red">
          {this.props.fallbackMessage || 'Что-то пошло не так при рендере этого компонента.'}
          {this.state.error && <pre style={{ whiteSpace: 'pre-wrap', marginTop: '10px', fontSize: '12px' }}>{this.state.error.toString()}</pre>}
        </Alert>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
