---
name: skill-travel-guide
description: Use when planning a leisure trip, city break, scenic-area visit, food-focused itinerary, multi-day route, weather backup, or an optional packaged mobile travel-guide website for a specific destination. 中文触发场景：旅行攻略、行程规划、citywalk、景区路线、多日游、本地美食推荐、雨天备选方案、旅游网站打包。
---

# skill_Travel-guide

## Overview

Build an executable trip from current evidence, route geometry, traveler constraints, and explicit priorities. Treat a claim as "locals recommend it" only when independent evidence supports that wording; popularity alone is not local endorsement.

## Non-negotiable Rules

- Default to a text guide. Generate a website only when the user explicitly asks for a website, web page, shareable page, package, or deployment.
- Research dynamic facts before arranging time blocks. Never invent opening hours, closures, prices, ratings, reservations, weather, travel times, shuttle schedules, or restaurant status.
- Label facts with source type and verification date. Mark unresolved facts as `待核实`; do not hide uncertainty behind "以现场为准".
- Include both neighborhood/local small eateries and established/formal restaurants when credible candidates exist. Do not fill the list with only famous chains, only social-media discoveries, or only tiny shops.
- Do not describe a restaurant as local-approved from one platform score, one influencer post, a promotional list, or the word `老字号` in its own name.
- Protect arrival and departure buffers before adding optional sights. Delete optional content rather than compressing transit or check-in time.
- Write executable Plan B triggers: name the condition, replacement, transport effect, and what gets dropped.

## 1. Normalize the Brief

Capture these facts in a compact trip card:

- destination and exact dates;
- arrival/departure station, airport, or self-drive boundary and times;
- traveler count, ages, mobility, pace, budget, dietary or cultural constraints;
- lodging location or preferred district;
- must-see places, explicit exclusions, and reservation status;
- allowed transport modes and taxi tolerance;
- food goals and formality needs.

Ask one high-impact question at a time only when its answer materially changes the route. Otherwise proceed with clearly labeled assumptions and state which blocks may change.

Convert relative dates such as "tomorrow" into absolute local dates. Detect impossible combinations early, including closed museums, late arrival, remote sights, and a departure buffer that leaves no usable morning.

## 2. Research Current Facts

Read [references/research-method.md](references/research-method.md) before using web search, map tools, weather tools, or route planners.

For mainland China, follow the "Preferred MCP Gate" in that reference: use Amap MCP and Xiaohongshu MCP when available; if either is missing, recommend installation and disclose the weaker evidence before falling back.

Use official attraction and transport sources for hours, closures, reservations, shuttle operations, and safety notices. Use maps for location and routing, not as the sole authority for cultural facts or temporary closures.

Research food as a separate evidence task. Read [references/food-evidence.md](references/food-evidence.md) whenever recommending named restaurants, stalls, markets, dishes, or meal areas.

## 3. Build Route Geometry

Cluster sights by district before assigning days. For every major move, record origin, destination, mode, typical duration, and a realistic buffer. Compare scenic shuttles, taxis, public transit, walking, and self-drive only among modes the user accepts.

Use a decision threshold rather than a rigid hierarchy. State when to stop waiting for a shuttle or queue and switch modes. Do not quote current route results as guaranteed future traffic conditions.

Prioritize the trip:

- `核心`: the destination-defining experiences;
- `重要`: valuable and route-compatible;
- `可选`: first to remove under delays, fatigue, weather, or failed reservations.

Do not spread time evenly. Give more time to the places that carry the trip's theme.

## 4. Write Each Day

For each block include time, place, transit, expected duration, purpose, and exit time. Set an explicit "start leaving" time for reservations and departures.

For every major attraction include:

- recommended viewing order;
- two to five specific highlights and why they matter;
- one practical viewing or photography technique;
- current closure, reservation, accessibility, and weather constraints;
- `time short`: what to keep and what to skip first.

Do not copy generic encyclopedia text. Connect the attraction to what the traveler should notice on site.

## 5. Place Meals Into the Route

Use meal-area fit before fame. For each important dining area, provide a primary and a nearby or route-compatible backup. Across the trip, include at least one credible `本地小馆` and one credible `成熟大饭店`; for a food-focused trip, include both types in each major dining cluster when evidence supports them.

Set a queue cutoff, explain what to order for the party size, and avoid repeated heavy dishes. If no candidate passes the evidence rules, recommend a dish or neighborhood instead of fabricating a restaurant.

## 6. Build Plan B

Cover the risks that can actually alter the route:

- ordinary rain versus severe-weather warning;
- attraction closure or failed reservation;
- shuttle cancellation, sold-out transport, or congestion;
- delayed arrival or early departure;
- restaurant closure, sell-out, or queue beyond cutoff;
- fatigue, mobility limits, or illness.

Keep Plan B geographically coherent. Recalculate transit and reservations after replacing a stop. Never place a typically closed indoor venue into a rain plan without verifying its opening day.

## 7. Deliver the Guide

Read [references/itinerary-output.md](references/itinerary-output.md) before writing the final guide, and see [references/example-day.md](references/example-day.md) for the target shape of one filled day. Match detail to the request: concise for a quick plan, fuller for a final itinerary, and exhaustive only when the user asks for all cautions and attraction tactics.

End with:

- reservation and purchase checklist;
- packing, weather, cultural etiquette, photography, health, luggage, and departure cautions;
- a dated "last verification" checklist;
- source list grouped by official, map/transport, weather, and food evidence.

## Optional Website Branch

Enter this branch only after an explicit website/package/deployment request. Read [references/optional-website.md](references/optional-website.md) before implementation. The text guide remains the source of truth; do not let presentation remove caveats, evidence labels, backups, or departure buffers.

## Quality Gate

Before delivering, verify every item:

- Exact dates and day-of-week match.
- Arrival and departure buffers are feasible.
- Route order follows geography and accepted transport modes.
- Dynamic claims have a source type and verification date.
- Amap MCP and Xiaohongshu MCP were used for a mainland-China trip when available; otherwise their absence, installation recommendation, and fallback were disclosed.
- Restaurant set includes small-local and established-formal categories, or explains why one category lacks credible evidence.
- Every named restaurant has route fit, signature dishes, queue risk, evidence basis, and a backup at the meal-slot level.
- Plan B states triggers and preserves route feasibility.
- Website work was not started without an explicit request.
- No unsupported superlatives, fake precision, or invented local consensus remain.

## Red Flags

Food-specific red flags live in [references/food-evidence.md](references/food-evidence.md). Trip-level red flags:

- listing restaurants without verification dates or route fit
- giving a rain alternative that is closed that day
- promising an exact future drive time from a current map result
- hiding all uncertainty in one generic disclaimer
- generating a landing page when the user requested only an itinerary
