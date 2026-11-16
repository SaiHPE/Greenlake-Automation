import { Grommet } from 'grommet';
import { createRoot } from 'react-dom/client';
import App from './App';
import { theme } from './theme';

createRoot(document.getElementById('root')!).render(
  <Grommet theme={theme} full>
    <App />
  </Grommet>,
);
