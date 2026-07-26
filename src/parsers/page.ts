import * as cheerio from "cheerio";
import { ContentError } from "../errors.js";
import type { PageContent, SearchResult } from "../types.js";
import { normalizeAllowedUrl } from "../client/url-policy.js";

export function parsePage(html: string, sourceUrl: string): PageContent {
  const $ = cheerio.load(html);
  $("script,style,noscript,nav,footer,header,[role='navigation'],[aria-label*='cookie' i]").remove();
  const title = clean($("main h1, article h1, h1").first().text() || $("title").text());
  const description = nullable($("meta[name='description']").attr("content") ?? "");
  const root = $("main").first().length ? $("main").first() : $("article").first().length ? $("article").first() : $("body");
  const body = clean(root.text()).slice(0, 20_000);
  if (!title || !body) {
    throw new ContentError("PARSE_FAILED", "The page has no recognizable title or main content.", "Open the source page directly; its structure may have changed.");
  }

  const links: SearchResult[] = [];
  const seen = new Set<string>();
  root.find("a[href]").each((_, element) => {
    if (links.length >= 50) return false;
    const anchor = $(element);
    try {
      const url = normalizeAllowedUrl(new URL(anchor.attr("href")!, sourceUrl));
      if (seen.has(url.href)) return;
      const linkTitle = clean(anchor.text() || anchor.attr("title") || "");
      if (!linkTitle) return;
      seen.add(url.href);
      links.push({ type: inferType(url.pathname), title: linkTitle, summary: null, imageUrl: null, sourceUrl: url.href });
    } catch {
      return;
    }
  });

  return { type: "collection", title, description, imageUrl: image($, sourceUrl), sourceUrl, body, links };
}

function image($: cheerio.CheerioAPI, baseUrl: string): string | null {
  const value = $("meta[property='og:image']").attr("content") ?? $("main img, article img").first().attr("src");
  return value ? new URL(value, baseUrl).href : null;
}

function inferType(path: string): SearchResult["type"] {
  const value = path.toLowerCase();
  if (/recipe|recipes|ricett/.test(value)) return "recipe";
  if (/video/.test(value)) return "video";
  if (/author/.test(value)) return "author";
  if (/article|news|magazine/.test(value)) return "article";
  return "collection";
}

function clean(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function nullable(value: string): string | null {
  return clean(value) || null;
}
