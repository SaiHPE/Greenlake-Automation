import { Grommet } from 'grommet';
import { hpe } from 'grommet-theme-hpe';
import { createRoot } from 'react-dom/client';
import App from './App';

createRoot(document.getElementById('root')!).render(
  <Grommet theme={hpe} full>
    <App />
  </Grommet>,
);
