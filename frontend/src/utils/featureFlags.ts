import { datadogRum } from '@datadog/browser-rum';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

let flagCache: Record<string, boolean> = {};

export async function initFeatureFlags(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/flags`);
    if (!response.ok) return;
    const flags = await response.json();
    flagCache = Object.fromEntries(
      Object.entries(flags).map(([key, val]: [string, any]) => [key, val.enabled ?? false])
    );
  } catch (e) {
    console.warn('Failed to load feature flags:', e);
  }
}

export function evaluateFlag(flagName: string, defaultValue: boolean = false): boolean {
  const value = flagCache[flagName] ?? defaultValue;
  try {
    datadogRum.addFeatureFlagEvaluation(flagName, value);
  } catch (e) {
    // RUM may not be initialized
  }
  return value;
}

export async function refreshFlags(): Promise<void> {
  await initFeatureFlags();
}
