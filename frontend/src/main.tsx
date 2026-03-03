import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { datadogRum } from '@datadog/browser-rum'
import { datadogLogs } from '@datadog/browser-logs'
import './index.css'
import App from './App.tsx'

const ddAppId = import.meta.env.VITE_DD_APP_ID
const ddClientToken = import.meta.env.VITE_DD_CLIENT_TOKEN

if (ddAppId && ddClientToken) {
  datadogLogs.init({
    clientToken: ddClientToken,
    site: import.meta.env.VITE_DD_SITE || 'datadoghq.com',
    service: 'travel-planner-frontend',
    env: import.meta.env.VITE_DD_ENV || 'dev',
    version: '1.0.0',
    forwardErrorsToLogs: true,
    forwardConsoleLogs: 'all',
    sessionSampleRate: 100,
  })

  datadogRum.init({
    applicationId: ddAppId,
    clientToken: ddClientToken,
    site: import.meta.env.VITE_DD_SITE || 'datadoghq.com',
    service: 'travel-planner-frontend',
    env: import.meta.env.VITE_DD_ENV || 'dev',
    version: '1.0.0',
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: 'mask-user-input',
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
