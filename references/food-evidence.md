# Food Evidence And Recommendation Rules

Use this reference for every named restaurant, stall, market, dish, food street, or meal plan.

## Maintain Two Tracks

Build a balanced set rather than one undifferentiated ranking.

| Track | Typical candidates | Best use | Main risk |
|---|---|---|---|
| `本地小馆` | neighborhood noodle shop, breakfast stall, family restaurant, market eatery, community canteen | breakfast, quick lunch, regional everyday food | variable hours, sell-outs, limited seating |
| `成熟大饭店` | established regional restaurant, historic brand, banquet restaurant, formal local-cuisine dining room | representative dinner, groups, elders, celebration | queues, oversized dishes, tourist-oriented branches |

Classify by actual operating style, not price alone. A chain can qualify only if the specific branch and regional relevance are supported. A hotel restaurant is not automatically local cuisine.

## What Counts As Local Evidence

Separate facts from interpretation:

- `Operational fact`: address, branch, hours, phone, price band, reservation method, current status.
- `Local-consumption signal`: repeated recent mentions of neighborhood repeat customers, local-language discussions, local editorial coverage, a long-running community presence, or consistent dish-level reviews across independent sources.
- `Social discovery`: an influencer post, short-video trend, Xiaohongshu note, platform ranking, or viral queue.

Call a place `本地口碑较强` only when current operational facts are verified and at least two independent local-consumption signals agree. Prefer signals from different source types. Do not count copied articles, reposts, or multiple branches of the same platform as independent.

When evidence is weaker, say `近期平台口碑较集中`, `老店线索`, or `社交平台发现`; do not upgrade it to "locals recommend".

## Search Procedure

Search in the destination's language and at district level. Useful Chinese queries include:

- `<城市> 本地人 吃什么`
- `<城市> 老店 当地菜`
- `<街区> 社区小馆`
- `<特色菜> 本地人 哪家`
- `<店名> 排队 避雷`
- `<店名> 搬迁 闭店 分店`

Use official/business channels and maps for operational facts. Use Meituan, Dianping, Xiaohongshu, local forums, local media, and short-video platforms as review/discovery evidence when accessible. Check recent negative reviews for closure, hygiene, forced packages, seafood pricing, inconsistent branches, and queue manipulation.

For a mainland-China trip, follow the MCP availability and fallback rules in `research-method.md`. Use Xiaohongshu MCP for dish vocabulary, community-shop leads, recent queues, branch changes, and avoidance reports, then use Amap MCP to resolve the exact branch, route fit, and nearby backups. Treat all Xiaohongshu results as one source family and cross-check them with business facts and at least one independent evidence type before claiming local endorsement.

Do not quote a platform score without its platform, branch, and check date. Scores across platforms are not directly comparable.

## Candidate Record

Record every named candidate in this form:

| Field | Required content |
|---|---|
| Name and exact branch | Avoid brand-only ambiguity |
| Track | `本地小馆` or `成熟大饭店` |
| Why it fits | Dish, meal, party, budget, and route reason |
| Signature order | What to order and sensible quantity |
| Address/area | Enough to confirm route compatibility |
| Current status | Hours/reservation/phone where verified |
| Price | Range with source and check date, or `待核实` |
| Queue risk | likely peak and explicit cutoff |
| Evidence | source types and what each supports |
| MCP trace | which Amap/Xiaohongshu queries informed the choice, or why either MCP was unavailable |
| Verified | absolute date |
| Caveat | branch, seasonal dish, sell-out, allergy, hygiene, or pricing issue |

Do not require every restaurant to have its own backup. Require every meal slot to have a route-compatible backup with the same practical role.

## Selection Rules

1. Start from the dish and meal area, then choose a venue.
2. Exclude places that force a major detour unless the user is food-first.
3. Prefer a smaller menu with repeated dish-level consensus over a generic high score.
4. For seafood, market, or weight-priced dishes, require price confirmation before ordering.
5. For two travelers, recommend a conservative first order and allow additions; do not prescribe banquet quantities.
6. Set a queue cutoff, commonly 20–30 minutes, adjusted for how replaceable the meal is.
7. If reliable evidence cannot support both tracks, explain the gap and recommend a dish/area rather than inventing a venue.

## Output Format

Present a compact table:

| Meal/area | Place and track | Why choose it | Order | Price/status | Evidence and checked date | Queue/backup |
|---|---|---|---|---|---|---|

Then state what the evidence does and does not prove. Keep discovery-only candidates out of the primary itinerary unless the user explicitly wants experimental options.

## Red Flags

- "评分高，所以本地人爱吃"
- "小红书很多人发，所以是当地老店"
- "网红但本地人也爱" without independent local evidence
- choosing a remote restaurant solely for a higher score
- mixing branches with different menus or quality histories
- repeating the same heavy specialty at multiple meals
- calling a newly opened shop a historic local institution
- recommending a queue without a cutoff or nearby backup
