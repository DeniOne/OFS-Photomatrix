import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Убираем MantineProvider и тему
// import { MantineProvider } from '@mantine/core'
// import theme from './styles/theme'
import './index.css'
// Убираем стили Mantine
// import '@mantine/core/styles.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* <MantineProvider theme={theme} defaultColorScheme="dark"> */}
      <App />
    {/* </MantineProvider> */}
  </StrictMode>,
)
