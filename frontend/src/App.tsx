import { ToastProvider } from './components/Toast';
import Chat from './views/Chat';
import './App.css';

function App() {
  return (
    <ToastProvider>
      <div className="App">
        <Chat />
      </div>
    </ToastProvider>
  );
}

export default App;
