# Research Method

Use this reference whenever current facts, maps, transport, weather, or web research affect the itinerary.

## Source Hierarchy

Use the strongest available source for each claim:

| Claim | Preferred source | Supporting source | Do not rely on alone |
|---|---|---|---|
| Opening, closure, ticket, reservation | attraction, museum, government, or official account | official ticket platform | old blogs or map snippets |
| Weather and warnings | meteorological authority or current forecast service | Amap weather or a second forecast | climate averages |
| Route, distance, mode comparison | Amap MCP or another current map planner | operator route page | straight-line distance |
| Scenic shuttle or direct bus | operator, official tourism platform, station notice | recent map or local report | an undated travel note |
| Rail or flight | operator, 12306, airline, or airport | current aggregator | cached search snippets |
| Restaurant address and hours | business official channel plus current map/listing | phone or recent platform status | an old listicle |
| Cultural significance | heritage authority, museum, or scholarly institution | reputable editorial source | influencer caption |

For conflicting sources, show the conflict and follow the more authoritative, more recent source. A map listing can confirm where a venue is; it cannot overrule an official closure notice.

## Preferred MCP Gate For Mainland China

Strongly recommend installing Amap MCP and Xiaohongshu MCP before a China itinerary research pass. Inspect available MCP tools by capability rather than assuming a fixed server name.

- Use **Amap MCP** for exact POI resolution, branch addresses, route planning, transit/walking/driving comparisons, weather, surrounding search, and geographic feasibility.
- Use **Xiaohongshu MCP** for food discovery, local dish vocabulary, neighborhood small-shop leads, recent queue conditions, branch-change warnings, tourist-trap avoidance, and negative experience patterns.

Use both when installed. Their outputs complement rather than replace official sources: Amap answers "where and how to get there"; Xiaohongshu supplies discovery and recent lived-experience signals; official sources settle openings, closures, tickets, warnings, and policy.

If either MCP is absent:

1. Tell the user that installing it is strongly recommended and state the missing benefit.
2. Offer the platform-supported installation path. In Claude Code, that is `claude mcp add <name> ...` or editing the MCP config, then checking `/mcp`; on other agent platforms, follow that platform's MCP configuration mechanism. Request manual approval, server details, or credentials when required; do not invent them.
3. If the user wants to continue without installation, use official web sources, current maps, business channels, and other local-life platforms and label the reduced evidence confidence.
4. Never claim that an unavailable MCP was called.

## Research Sequence

1. Resolve exact place names and districts. Disambiguate duplicate POIs.
2. Verify official hours, closed weekdays, seasonal rules, reservations, last entry, temporary closures, and safety notices.
3. Check the forecast for each exact travel date and record the forecast issue/access date.
4. Query routes between actual anchors: arrival point, lodging, sights, dining areas, and departure point.
5. Check tourist shuttles and direct services separately from ordinary public transit.
6. Research food with the separate evidence procedure.
7. Re-check dependencies after drafting: a changed attraction must also update meals, routes, and Plan B.

## China Map Workflow

When Amap MCP is available:

- Geocode lodging and POIs before routing.
- Use the requested transport mode; do not silently substitute driving for public transit.
- Query public transit with the correct city and local date/time where supported.
- Compare walking distance to station access, transfer count, total time, service end time, and taxi cost band when available.
- Link to the exact POI or map search in the guide when useful.
- Treat route duration as an estimate. Add seasonal, weather, crowd, transfer, and pickup buffers explicitly.

If Amap MCP is unavailable, strongly recommend installing it, state that limitation, and use current official transport sources plus a map service accessible through the available tools. Never imply an unavailable MCP was used.

## Xiaohongshu MCP Workflow

Use Xiaohongshu MCP as a discovery and risk-sensing layer, not a restaurant truth database.

- Search by `city + district + dish`, then repeat with `本地人`, `社区小馆`, `老店`, `排队`, `搬店`, and `避雷`.
- Prefer recent posts with concrete branch, dish, price, wait, and visit details. Capture publication date and exact claims.
- Look for disagreements, suspected promotion, copied wording, and branch confusion.
- Do not infer that an author is local from tone, IP labels, or one self-description.
- Cross-check each shortlisted venue's exact branch, location, and route fit with Amap MCP; verify current operations through business channels or a second current platform.
- Count multiple Xiaohongshu notes as one source family when assessing independence. They can strengthen a pattern but cannot alone establish `本地口碑较强`.

## Freshness Labels

Attach an access or verification date to dynamic facts.

- `已核实 YYYY-MM-DD`: supported by a current source.
- `出发前复核`: likely to change, such as forecast, shuttle seat inventory, performance schedule, restaurant queue, or temporary closure.
- `待核实`: evidence is incomplete or conflicting.
- `仅作发现线索`: social or secondary source found the candidate but does not prove the claim.

Recheck weather and warnings within 72 hours and again on the travel morning. Recheck transport seat inventory, performance schedules, temporary closures, and restaurant hours as close to use as practical.

## Evidence Notes

Keep a compact fact ledger during research:

| Fact | Value | Source type | Source/link | Checked | Confidence/next action |
|---|---|---|---|---|---|

Do not expose a long research dump by default. Surface citations next to high-impact claims, then provide a grouped source list at the end.

## Failure Handling

- If search results are inaccessible, do not infer their content from snippets beyond what the snippet actually states.
- If Xiaohongshu MCP is unavailable, recommend installation and label social-discovery coverage as incomplete rather than reconstructing posts from snippets.
- If a source lacks a date, lower confidence and seek a second source.
- If official and platform hours differ, call or mark `出发前复核`; do not pick whichever fits the plan.
- If no safe route exists within the time window, remove the stop.
- If weather is beyond a reliable forecast horizon, use seasonal risk only and schedule a dated recheck; do not present a forecast.
