import type {
  ArticleContent,
  AuthorContent,
  Content,
  ContentType,
  PageContent,
  RecipeContent,
  SearchResult,
  VideoContent,
} from "../types.js";
import { normalizeAllowedUrl } from "../client/url-policy.js";
import { parseArticle, parseAuthor, parseRecipe, parseVideo } from "../parsers/content.js";
import { parsePage } from "../parsers/page.js";
import { buildSearchUrl, parseSearchResults } from "../parsers/search.js";

interface HtmlClient {
  getHtml(url: string | URL): Promise<string>;
}

interface CacheStore {
  get(key: string): unknown;
  set(key: string, value: unknown): void;
}

export class ContentService {
  constructor(private readonly http: HtmlClient, private readonly cache: CacheStore) {}

  async search(query: string, type: ContentType | "all", limit: number): Promise<SearchResult[]> {
    const url = buildSearchUrl(query.trim());
    const key = `search:${query.trim().toLowerCase()}:${type}:${limit}`;
    const cached = this.cache.get(key) as SearchResult[] | undefined;
    if (cached) return cached;
    const result = parseSearchResults(await this.http.getHtml(url), url.href, type, limit);
    this.cache.set(key, result);
    return result;
  }

  getRecipe(url: string): Promise<RecipeContent> {
    return this.detail("recipe", url, parseRecipe);
  }

  getArticle(url: string): Promise<ArticleContent> {
    return this.detail("article", url, parseArticle);
  }

  getVideo(url: string): Promise<VideoContent> {
    return this.detail("video", url, parseVideo);
  }

  getAuthor(url: string): Promise<AuthorContent> {
    return this.detail("author", url, parseAuthor);
  }

  getPage(url: string): Promise<PageContent> {
    return this.detail("page", url, parsePage);
  }

  private async detail<T extends Content>(
    operation: string,
    input: string,
    parser: (html: string, sourceUrl: string) => T,
  ): Promise<T> {
    const url = normalizeAllowedUrl(input);
    const key = `${operation}:${url.href}`;
    const cached = this.cache.get(key) as T | undefined;
    if (cached) return cached;
    const result = parser(await this.http.getHtml(url), url.href);
    this.cache.set(key, result);
    return result;
  }
}
