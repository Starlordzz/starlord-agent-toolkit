export class RateLimiter {
  private nextStart = 0;
  private queue: Promise<void> = Promise.resolve();

  constructor(
    private readonly intervalMs: number,
    private readonly now: () => number = Date.now,
    private readonly sleep: (ms: number) => Promise<void> = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  ) {}

  wait(): Promise<void> {
    const turn = this.queue.then(async () => {
      const delay = Math.max(0, this.nextStart - this.now());
      if (delay > 0) await this.sleep(delay);
      this.nextStart = this.now() + this.intervalMs;
    });
    this.queue = turn.catch(() => undefined);
    return turn;
  }
}
