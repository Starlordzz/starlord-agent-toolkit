# AI Generation & Risk Disclosure

**English** | [简体中文](./AI-DISCLOSURE.zh-CN.md)

> This document is provided in English and Chinese. The two versions are intended to match; if they diverge, the [Chinese version](./AI-DISCLOSURE.zh-CN.md) prevails. The formal terms of the LICENSE take precedence over either language version of this disclosure.

## 1. How This Project Was Created

The initial architecture, source code, tests, build configuration, MCP tool definitions, and documentation of this project were generated primarily by AI coding agents from natural-language requirements provided by the maintainer. The maintainer took part in requirement confirmation, design selection, tool authorization, test execution, troubleshooting, and partial review of the output.

"Human involvement" does not mean "fully human-written or line-by-line audited". Unless explicitly recorded otherwise, any file in this repository may contain content created or modified directly by generative AI.

## 2. Inherent Limitations of AI-Generated Content

Generative AI can produce problems including, but not limited to:

- implementations that are syntactically correct but logically wrong;
- uncovered edge cases, concurrency issues, resource leaks, or security flaws;
- inaccurate understanding of third-party page structures, protocols, APIs, or legal requirements;
- outdated, fabricated, incomplete, or mutually contradictory information;
- code incompatible with dependency versions, runtime environments, or future site changes;
- unintentionally generated expression or implementations similar to existing works;
- insufficient test coverage, or tests that do not match real-world usage.

Therefore, the fact that the repository runs, tests pass, or examples succeed must not be interpreted as a guarantee of quality, security, legality, or fitness for purpose.

## 3. Boundaries of Human Review and Testing

During development, the project ran TypeScript builds, offline automated tests, and limited live smoke tests against the real website. These checks only cover the specific code version, dependency versions, page samples, and network environment present at the time they ran.

The project does **not** claim to have completed any of the following:

- an independent professional security audit or penetration test;
- human review of every line of code;
- compatibility testing against all GialloZafferano page types and historical pages;
- professional review of legal, copyright, trademark, privacy, data-protection, or site-terms matters;
- professional verification of food-safety, allergen, nutrition, or medical information;
- testing across all operating systems, MCP clients, and Node.js versions.

## 4. The User's Verification Responsibilities

Before using, modifying, deploying, publicly offering, or distributing this project, users should independently:

- read and understand the source code, dependencies, and configuration;
- run the tests and add tests for their actual use case;
- perform security, privacy, and compliance reviews;
- check the target site's terms of use, robots rules, and access restrictions;
- check third-party content, trademark, and copyright permissions;
- read and comply with the AGPLv3, including the source-offer obligations that apply to modification, distribution, and remote network interaction;
- independently verify recipes, allergens, nutrition, servings, times, and food-safety information;
- set up monitoring, rate limiting, failure recovery, and human review for production or otherwise important environments.

## 5. No Professional Advice

This project and its output do not constitute legal, compliance, security, privacy, nutrition, medical, food-safety, or other professional advice. Neither the maintainer nor any AI system is the user's lawyer, auditor, doctor, dietitian, or security consultant.

## 6. No Official Relationship or Endorsement

This project is not an official GialloZafferano product. The maintainer has no affiliation, partnership, authorization, sponsorship, or endorsement relationship with GialloZafferano, its owners, affiliates, employees, authors, or content creators. The project name is used only to describe compatibility and the targeted data source.

GialloZafferano's name, trademarks, pages, images, videos, recipes, articles, and other content belong to their respective rights holders. This repository's license grants no rights to any third-party content or trademarks.

## 7. Data and Operational Risks

Third-party websites may change their structure, content, URLs, access policies, or technical protection measures at any time. As a result, this project may return empty results, wrong fields, outdated data, or parse failures, and may trigger third-party rate limiting or access restrictions.

Users must not rely on this project to bypass CAPTCHAs, logins, access controls, paywalls, rate limits, or other technical protection measures. Liability arising from a user's deployment style, request volume, or data handling rests with that user.

## 8. No Warranty and Limitation of Liability

This project is provided as-is, without any express or implied warranty, including but not limited to warranties of correctness, completeness, availability, security, continued compatibility, merchantability, non-infringement, or fitness for a particular purpose.

To the maximum extent permitted by applicable law, the maintainer is not liable for any direct, indirect, incidental, special, punitive, or consequential damages arising from this project or its output, including data loss, lost profits, business interruption, account or IP restrictions, third-party claims, compliance penalties, or food or health harm.

The formal license and liability terms in the LICENSE take precedence over this disclosure document. This document exists to improve transparency; it does not replace applicable law and is not legal advice.

## 9. Reporting Issues

If you find a security, copyright, trademark, privacy, data-accuracy, or other issue, contact the maintainer via a GitHub Issue. Before reporting a security issue publicly, avoid disclosing sensitive details that could be directly exploited.
