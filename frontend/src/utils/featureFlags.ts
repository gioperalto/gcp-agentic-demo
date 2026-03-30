import { DatadogProvider } from '@datadog/openfeature-browser';
import { OpenFeature } from '@openfeature/react-sdk';

let initialized = false;

export async function initFeatureFlags(): Promise<void> {
  if (initialized) return;

  const appId = import.meta.env.VITE_DD_APP_ID;
  const clientToken = import.meta.env.VITE_DD_CLIENT_TOKEN;
  const site = import.meta.env.VITE_DD_SITE || 'datadoghq.com';
  const env = import.meta.env.VITE_DD_ENV || 'dev';

  if (!appId || !clientToken) {
    console.warn('Datadog Feature Flags: missing DD_APP_ID or DD_CLIENT_TOKEN');
    return;
  }

  try {
    const provider = new DatadogProvider({
      applicationId: appId,
      clientToken: clientToken,
      site: site,
      env: env,
    });

    await OpenFeature.setProviderAndWait(provider);
    initialized = true;
    console.log('Datadog Feature Flags initialized via OpenFeature SDK');
  } catch (e) {
    console.warn('Failed to initialize Datadog Feature Flags:', e);
  }
}

/**
 * Update the OpenFeature evaluation context (e.g., after login).
 * Context attributes must be flat primitives (string, number, boolean).
 */
export async function setFeatureFlagContext(context: Record<string, string | number | boolean>): Promise<void> {
  try {
    await OpenFeature.setContext(context);
  } catch (e) {
    console.warn('Failed to set feature flag context:', e);
  }
}
