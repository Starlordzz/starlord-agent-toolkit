# Optional Website Output

Read this file only when the user explicitly asks for a website, shareable page, package, or deployment.

## Scope Gate

Do not generate website files for a normal travel-planning request. If the user says the site is optional, deliver the text guide first and offer or build the site only when they select that option.

The verified guide is the content source of truth. Preserve dates, evidence labels, Plan B triggers, exclusions, and departure buffers in the interface.

## Default Technical Shape

Prefer a static, mobile-first site with plain HTML, CSS, and JavaScript unless the existing repository already uses a framework. Keep external runtime dependencies and images minimal.

For a self-hosted package without Docker, default to:

- static guide files;
- a dependency-free Node static server when direct file hosting is insufficient;
- `/health` and `/healthz` endpoints;
- `deploy.sh` that installs or verifies prerequisites, starts/restarts the service, and prints the URL;
- one-command Linux deployment such as `bash deploy.sh`;
- a ZIP whose top level is one named project directory.

Confirm the user's actual deployment target first. If it is Windows or macOS rather than Linux, adapt the script form (e.g. `deploy.ps1` or platform-neutral `npm` scripts) instead of shipping a Linux-only `deploy.sh`.

Never put Amap or other private API keys in browser JavaScript. Use public map deep links, a server-side proxy, or clearly documented user-supplied configuration.

## Information Architecture

Open on the usable guide, not a marketing landing page. Recommended sections:

1. trip summary with date, weather status, lodging area, and key decisions;
2. day switcher and chronological itinerary;
3. attraction tactics with `core/important/optional` priority;
4. food filters for `本地小馆` and `成熟大饭店` plus evidence status;
5. route and map deep links;
6. Plan B decision matrix;
7. reservations and saved checklist;
8. source and last-verified panel.

Use day tabs, checkboxes, toggles, and icon buttons for their natural roles. Do not nest cards inside cards. Keep tap targets at least 44 px, body text readable, and fixed controls dimensionally stable.

## Useful Features

Include only features that help during the trip:

- day filtering without layout shift;
- checklist persistence with `localStorage`;
- click-to-open map directions;
- clear primary/backup restaurant states and queue cutoff;
- print/PDF stylesheet;
- offline-friendly static content where practical;
- visible verification dates and `待核实` markers.

Do not add accounts, analytics, CMS, or live APIs unless requested.

## Visual Direction

Derive color and typography from the destination without turning the page into a themed poster. Use one strong destination image or a small number of inspectable images; do not depend on image quantity. Avoid gradients, decorative blobs, oversized mobile headings, tourist-brochure card walls, and text describing how to use the page.

Keep the interface dense enough for repeated reference outdoors. Make emergency decisions, departure time, weather status, and Plan B easy to scan.

## Package Checklist

- All files are complete; no placeholders or sample destinations remain.
- Relative asset paths work inside the ZIP.
- The archive opens into one top-level folder.
- `bash deploy.sh` works on the target Linux assumptions and does not require Docker.
- The server rejects path traversal and returns correct content types.
- `/health` and `/healthz` return success.
- README/DEPLOY instructions belong to the generated website package, not to this Skill folder.
- No secret, local absolute path, private token, or research scratch file is packaged.

## Visual Verification

Before delivery:

1. Run the content/unit tests.
2. Start the local server.
3. Check at least a 390 x 844 mobile viewport and one desktop viewport with Playwright screenshots.
4. Verify no overlap, clipped text, horizontal overflow, blank image, broken link, or unusable tap target.
5. Exercise day filters, checklists, map links, print view, and health endpoints.
6. Inspect the final ZIP contents and run the deployment command in a clean temporary directory when feasible.

