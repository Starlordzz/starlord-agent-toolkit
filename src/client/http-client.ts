import { ContentError } from "../errors.js";
import { normalizeAllowedUrl } from "./url-policy.js";

interface HttpClientConfig {
  requestTimeoutMs: number;
  maxResponseBytes: number;
  userAgent: string;
}

interface Waiter {
  wait(): Promise<void>;
}

const REDIRECT_STATUSES = new Set([301, 302, 303, 307, 308]);

export class RestrictedHttpClient {
  constructor(
    private readonly config: HttpClientConfig,
    private readonly fetchImpl: typeof fetch = fetch,
    private readonly limiter: Waiter = { wait: async () => undefined },
    private readonly sleep: (ms: number) => Promise<void> = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  ) {}

  async getHtml(input: string | URL): Promise<string> {
    let url = normalizeAllowedUrl(input);
    let redirects = 0;

    for (;;) {
      const response = await this.fetchWithRetry(url);
      if (REDIRECT_STATUSES.has(response.status)) {
        if (++redirects > 5) {
          throw new ContentError("UPSTREAM_UNAVAILABLE", "Too many redirects.", "Open the source page and verify its current URL.");
        }
        const location = response.headers.get("location");
        if (!location) {
          throw new ContentError("UPSTREAM_UNAVAILABLE", "The redirect has no destination.", "Try the canonical page URL.");
        }
        url = normalizeAllowedUrl(new URL(location, url));
        continue;
      }
      return this.readHtmlResponse(response);
    }
  }

  private async fetchWithRetry(url: URL): Promise<Response> {
    for (let attempt = 0; attempt < 3; attempt++) {
      await this.limiter.wait();
      try {
        const response = await this.fetchImpl(url, {
          redirect: "manual",
          signal: AbortSignal.timeout(this.config.requestTimeoutMs),
          headers: { accept: "text/html,application/xhtml+xml", "user-agent": this.config.userAgent },
        });
        if (response.status >= 500 && attempt < 2) {
          await this.sleep(100 * (attempt + 1));
          continue;
        }
        if (response.status === 429 && attempt === 0) {
          const delay = retryAfterMs(response.headers.get("retry-after"));
          if (delay !== null && delay <= 2_000) {
            await this.sleep(delay);
            continue;
          }
        }
        return response;
      } catch (cause) {
        if (attempt < 2) {
          await this.sleep(100 * (attempt + 1));
          continue;
        }
        throw new ContentError("UPSTREAM_UNAVAILABLE", "The upstream request failed or timed out.", "Retry later or open the source page directly.", { cause });
      }
    }
    throw new ContentError("UPSTREAM_UNAVAILABLE", "The upstream request failed.", "Retry later.");
  }

  private async readHtmlResponse(response: Response): Promise<string> {
    if (response.status === 404) {
      throw new ContentError("NOT_FOUND", "The page was not found.", "Check that the source URL is current.");
    }
    if (response.status === 403 || response.status === 429) {
      throw new ContentError("UPSTREAM_BLOCKED", `The upstream site returned HTTP ${response.status}.`, "Wait before retrying or open the page directly.");
    }
    if (response.status >= 500 || !response.ok) {
      throw new ContentError("UPSTREAM_UNAVAILABLE", `The upstream site returned HTTP ${response.status}.`, "Retry later.");
    }

    const contentType = response.headers.get("content-type")?.toLowerCase() ?? "";
    if (!contentType.includes("text/html") && !contentType.includes("application/xhtml+xml")) {
      throw new ContentError("PARSE_FAILED", "The response is not an HTML page.", "Use a public GialloZafferano content page URL.");
    }
    const declaredLength = Number(response.headers.get("content-length"));
    if (Number.isFinite(declaredLength) && declaredLength > this.config.maxResponseBytes) {
      throw tooLarge();
    }

    if (!response.body) return "";
    const reader = response.body.getReader();
    const chunks: Uint8Array[] = [];
    let total = 0;
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > this.config.maxResponseBytes) {
        await reader.cancel();
        throw tooLarge();
      }
      chunks.push(value);
    }
    const bytes = new Uint8Array(total);
    let offset = 0;
    for (const chunk of chunks) {
      bytes.set(chunk, offset);
      offset += chunk.byteLength;
    }
    return new TextDecoder().decode(bytes);
  }
}

function retryAfterMs(value: string | null): number | null {
  if (!value) return null;
  const seconds = Number(value);
  if (Number.isFinite(seconds) && seconds >= 0) return seconds * 1_000;
  const date = Date.parse(value);
  return Number.isNaN(date) ? null : Math.max(0, date - Date.now());
}

function tooLarge(): ContentError {
  return new ContentError("PARSE_FAILED", "The response exceeds the configured size limit.", "Use a smaller content page.");
}
