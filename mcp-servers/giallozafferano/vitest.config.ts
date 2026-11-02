import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    clearMocks: true,
    exclude: ["dist/**", "node_modules/**"],
  },
});
