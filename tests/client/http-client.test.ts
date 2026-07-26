import { describe, expect, it, vi } from "vitest";
import { RestrictedHttpClient } from "../../src/client/http-client.js";

const config = {
  requestTimeoutMs: 100,
  maxResponseBytes: 32,
  userAgent: "test-agent",
};

function makeClient(fetchImpl: typeof fetch) {
  return new RestrictedHttpClient(config, fetchImpl, { wait: async () => undefined }, async () => undefined);
}

describe("RestrictedHttpClient", () => {
  it("returns HTML from an allowed URL", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(new Response("<main>ok</main>", {
      status: 200,
      headers: { "content-type": "text/html" },
    }));
    await expect(makeClient(fetchImpl).getHtml("https://www.giallozafferano.com/x")).resolves.toBe("<main>ok</main>");
  });

  it("rejects an off-site redirect before following it", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(new Response(null, {
      status: 302,
      headers: { location: "https://evil.test/x" },
    }));
    await expect(makeClient(fetchImpl).getHtml("https://www.giallozafferano.com/x"))
      .rejects.toMatchObject({ code: "SECURITY_REJECTED" });
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it.each([
    [404, "NOT_FOUND"],
    [403, "UPSTREAM_BLOCKED"],
    [429, "UPSTREAM_BLOCKED"],
    [500, "UPSTREAM_UNAVAILABLE"],
  ])("maps HTTP %i to %s", async (status, code) => {
    const fetchImpl = vi.fn().mockResolvedValue(new Response("error", { status }));
    await expect(makeClient(fetchImpl).getHtml("https://www.giallozafferano.com/x"))
      .rejects.toMatchObject({ code });
  });

  it("rejects non-HTML content", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(new Response("{}", {
      status: 200,
      headers: { "content-type": "application/json" },
    }));
    await expect(makeClient(fetchImpl).getHtml("https://www.giallozafferano.com/x"))
      .rejects.toMatchObject({ code: "PARSE_FAILED" });
  });

  it("rejects responses larger than the configured limit", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(new Response("x".repeat(33), {
      status: 200,
      headers: { "content-type": "text/html" },
    }));
    await expect(makeClient(fetchImpl).getHtml("https://www.giallozafferano.com/x"))
      .rejects.toMatchObject({ code: "PARSE_FAILED" });
  });
});
