export type ContentType =
  | "recipe"
  | "article"
  | "video"
  | "author"
  | "collection";

export interface SearchResult {
  type: ContentType;
  title: string;
  summary: string | null;
  imageUrl: string | null;
  sourceUrl: string;
}

interface BaseContent {
  title: string;
  description: string | null;
  imageUrl: string | null;
  sourceUrl: string;
}

export interface RecipeContent extends BaseContent {
  type: "recipe";
  servings: string | null;
  prepTime: string | null;
  cookTime: string | null;
  totalTime: string | null;
  difficulty: string | null;
  ingredients: string[];
  instructions: string[];
  nutrition: Record<string, string>;
  author: string | null;
}

export interface ArticleContent extends BaseContent {
  type: "article";
  body: string;
  author: string | null;
  datePublished: string | null;
  dateModified: string | null;
  related: SearchResult[];
}

export interface VideoContent extends BaseContent {
  type: "video";
  duration: string | null;
  uploadDate: string | null;
  author: string | null;
  embedUrl: string | null;
}

export interface AuthorContent extends BaseContent {
  type: "author";
  contents: SearchResult[];
}

export interface PageContent extends BaseContent {
  type: "collection";
  body: string;
  links: SearchResult[];
}

export type Content =
  | RecipeContent
  | ArticleContent
  | VideoContent
  | AuthorContent
  | PageContent;
