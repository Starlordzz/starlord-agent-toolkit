import * as cheerio from "cheerio";
import type { ContentType, SearchResult } from "../types.js";
import { normalizeAllowedUrl } from "../client/url-policy.js";

export function buildSearchUrl(query: string): URL {
  const cleaned = query.trim().toLowerCase().replace(/[-_/\s]+/g, "+");
  const encoded = encodeURIComponent(cleaned).replace(/%2B/g, "+");
  return new URL(`/recipes-search/${encoded}/`, "https://www.giallozafferano.com");
}

export function parseSearchResults(
  html: string,
  baseUrl: string,
  contentType: ContentType | "all",
  limit: number,
): SearchResult[] {
  const $ = cheerio.load(html);
  const output: SearchResult[] = [];
  const seen = new Set<string>();
  const candidates = $("article, [data-content-type], [class*='search-result']");

  candidates.each((_, element) => {
    if (output.length >= limit) return false;
    const root = $(element);
    const anchor = root.find("a[href]").first();
    const href = anchor.attr("href");
    if (!href) return;
    let source: URL;
    try {
      source = normalizeAllowedUrl(new URL(href, baseUrl));
    } catch {
      return;
    }
    if (seen.has(source.href)) return;
    const title = clean(root.find("h1,h2,h3,h4").first().text() || anchor.attr("title") || anchor.text());
    if (!title) return;
    const type = inferType(root.attr("data-content-type"), source.pathname);
    if (contentType !== "all" && type !== contentType) return;
    seen.add(source.href);
    const image = root.find("img").first().attr("src") ?? root.find("img").first().attr("data-src");
    output.push({
      type,
      title,
      summary: nullable(root.find(".gz-description,p").first().text()),
      imageUrl: image ? new URL(image, baseUrl).href : null,
      sourceUrl: source.href,
    });
  });
  return output;
}

function inferType(hint: string | undefined, path: string): ContentType {
  const value = `${hint ?? ""} ${path}`.toLowerCase();
  if (/recipes-list|latest-recipes/.test(value)) return "collection";
  if (/recipe|recipes|ricett/.test(value)) return "recipe";
  if (/video/.test(value)) return "video";
  if (/author|authors|editor/.test(value)) return "author";
  if (/article|news|magazine/.test(value)) return "article";
  return "collection";
}

function clean(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function nullable(value: string): string | null {
  return clean(value) || null;
}
