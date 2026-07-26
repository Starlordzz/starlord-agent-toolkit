import { ContentError } from "../errors.js";

export function isAllowedHostname(hostname: string): boolean {
  const normalized = hostname.toLowerCase().replace(/\.$/, "");
  return normalized === "giallozafferano.com" || normalized.endsWith(".giallozafferano.com");
}

export function normalizeAllowedUrl(input: string | URL): URL {
  let url: URL;
  try {
    url = input instanceof URL ? new URL(input.href) : new URL(input);
  } catch (cause) {
    throw new ContentError("INVALID_INPUT", "The URL is invalid.", "Provide a complete GialloZafferano HTTPS URL.", { cause });
  }

  if (url.protocol !== "https:" || url.username || url.password || !isAllowedHostname(url.hostname)) {
    throw new ContentError(
      "SECURITY_REJECTED",
      "Only credential-free HTTPS URLs on giallozafferano.com are allowed.",
      "Use the original public GialloZafferano page URL.",
    );
  }
  url.hash = "";
  return url;
}
