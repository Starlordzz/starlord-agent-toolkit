export interface AppConfig {
  requestTimeoutMs: number;
  maxResponseBytes: number;
  cacheMaxEntries: number;
  cacheTtlMs: number;
  minRequestIntervalMs: number;
  userAgent: string;
}

export const DEFAULT_CONFIG: Readonly<AppConfig> = {
  requestTimeoutMs: 10_000,
  maxResponseBytes: 2_000_000,
  cacheMaxEntries: 100,
  cacheTtlMs: 300_000,
  minRequestIntervalMs: 500,
  userAgent: "mcp-server-giallozafferano/0.1 (+read-only public content)",
};
