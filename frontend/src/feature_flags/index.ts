import { useBooleanFlagValue } from '@openfeature/react-sdk';

/**
 * Registry of all Datadog feature flags used in this application.
 * Keys are the flag names as defined in Datadog Feature Management.
 * Values are the default (fallback) values used when the flag is unavailable.
 *
 * Add new flags here — one entry per flag.
 */
export const FEATURE_FLAGS = {
  insecure_profile_agent: false,
  ralph_agent: false,
} as const;

export type FeatureFlagKey = keyof typeof FEATURE_FLAGS;

// --- Per-flag hooks ---

export const useInsecureProfileAgent = () =>
  useBooleanFlagValue('insecure_profile_agent', FEATURE_FLAGS.insecure_profile_agent);

export const useRalphAgent = () =>
  useBooleanFlagValue('ralph_agent', FEATURE_FLAGS.ralph_agent);
