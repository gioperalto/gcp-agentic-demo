import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { datadogRum } from '@datadog/browser-rum'
import { datadogLogs } from '@datadog/browser-logs'
import { initFeatureFlags } from './utils/featureFlags'
import './index.css'
import App from './App.tsx'

const ddAppId = import.meta.env.VITE_DD_APP_ID
const ddClientToken = import.meta.env.VITE_DD_CLIENT_TOKEN
const ddSite = import.meta.env.VITE_DD_SITE || 'datadoghq.com'
const ddService = import.meta.env.VITE_DD_SERVICE || 'travel-planner-frontend'
const ddEnv = import.meta.env.VITE_DD_ENV || 'dev'
const ddVersion = import.meta.env.VITE_DD_VERSION || '1.0.0'

if (ddAppId && ddClientToken) {
  datadogLogs.init({
    clientToken: ddClientToken,
    site: ddSite,
    service: ddService,
    env: ddEnv,
    version: ddVersion,
    forwardErrorsToLogs: true,
    forwardConsoleLogs: 'all',
    sessionSampleRate: 100,
  })

  datadogRum.init({
    applicationId: ddAppId,
    clientToken: ddClientToken,
    site: ddSite,
    service: ddService,
    env: ddEnv,
    version: ddVersion,
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: 'mask-user-input',
    allowedTracingUrls: [
      { match: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000', propagatorTypes: ['datadog', 'tracecontext'] },
    ],
  })
}

initFeatureFlags().catch(console.error);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
