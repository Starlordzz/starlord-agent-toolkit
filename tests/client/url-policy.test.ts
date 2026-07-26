import { describe, expect, it } from "vitest";
import { ContentError } from "../../src/errors.js";
import { normalizeAllowedUrl } from "../../src/client/url-policy.js";

describe("normalizeAllowedUrl", () => {
  it("accepts the root domain and its subdomains", () => {
    expect(normalizeAllowedUrl("https://giallozafferano.com/x").hostname).toBe("giallozafferano.com");
    expect(normalizeAllowedUrl("https://www.giallozafferano.com/x").hostname).toBe("www.giallozafferano.com");
  });

  it.each([
    "http://www.giallozafferano.com/x",
    "https://giallozafferano.com@evil.test/x",
    "https://evilgiallozafferano.com/x",
    "https://example.com/x",
    "file:///tmp/x",
  ])("rejects unsafe URL %s", (url) => {
    expect(() => normalizeAllowedUrl(url)).toThrowError(ContentError);
  });
});
