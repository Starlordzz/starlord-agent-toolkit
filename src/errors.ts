export type ContentErrorCode =
  | "INVALID_INPUT"
  | "SECURITY_REJECTED"
  | "NOT_FOUND"
  | "UPSTREAM_BLOCKED"
  | "UPSTREAM_UNAVAILABLE"
  | "TYPE_MISMATCH"
  | "PARSE_FAILED";

export class ContentError extends Error {
  constructor(
    public readonly code: ContentErrorCode,
    message: string,
    public readonly suggestion: string,
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.name = "ContentError";
  }
}
