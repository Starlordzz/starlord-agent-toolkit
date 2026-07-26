#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { DEFAULT_CONFIG } from "./config.js";
import { MemoryCache } from "./client/memory-cache.js";
import { RateLimiter } from "./client/rate-limiter.js";
import { RestrictedHttpClient } from "./client/http-client.js";
import { ContentService } from "./services/content-service.js";
import { createServer } from "./server.js";

const cache = new MemoryCache<unknown>(DEFAULT_CONFIG.cacheMaxEntries, DEFAULT_CONFIG.cacheTtlMs);
const limiter = new RateLimiter(DEFAULT_CONFIG.minRequestIntervalMs);
const http = new RestrictedHttpClient(DEFAULT_CONFIG, fetch, limiter);
const service = new ContentService(http, cache);
const server = createServer(service);

const close = async () => {
  await server.close();
  process.exit(0);
};
process.once("SIGINT", close);
process.once("SIGTERM", close);

server.connect(new StdioServerTransport()).catch((error: unknown) => {
  console.error("Failed to start GialloZafferano MCP server:", error);
  process.exit(1);
});
