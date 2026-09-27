# Keyword Research Reference (blog-brief Step 2)

## SERP request (Step 2a)

Tool: `mcp__dataforseo__api_request`. Exactly one call per run; retry once
only if the call returns an error.

```json
{
  "method": "POST",
  "path": "/v3/serp/google/organic/live/advanced",
  "noAiMode": true,
  "data": [{
    "keyword": "<focus keyword>",
    "location_code": 2840,
    "language_code": "en",
    "depth": 10,
    "load_async_ai_overview": true
  }]
}
```

- `noAiMode: true` is required: the default AI-mode response drops `cost` and
  `item_types`.
- Location and language default to United States / English (K-013). Use
  another only when the user's request names one.
- Read from the response: `cost` (top level), `tasks[0].result[0].item_types`,
  and `tasks[0].result[0].items`.
- Organic results are items with `type` `organic`; their rank is `rank_group`.
  Page 1 often has fewer than 10. Do not request more pages to fill the gap.
- People Also Ask: `items[type=people_also_ask].items[].title`.
  Related searches: `items[type=related_searches].items[]` (strings).
- AI Overview is present when `item_types` contains `ai_overview`.

## Page types

Classify each organic result from its URL, domain, and title. Do not fetch
the pages. Use exactly one of these values in the table:

| Value | What it is | Examples |
|---|---|---|
| `blog/guide` | An article that answers the query with information or ideas: blog posts, listicles, how-to guides, magazine articles. Guide articles on store domains count here | `cinapse.co/easy-costumes-...`, `halloweencostumes.com/.../costume-guide` |
| `category` | A page listing many products for sale: store category pages and store search result pages | `amazon.com/.../s?k=...`, `walmart.com/c/...`, `target.com/s/...`, `ebay.com/b/...` |
| `product` | A single product's sales page | `spirithalloween.com/product/...`, `costumes.com/products/...` |
| `other: <what>` | Anything else; name it: `video`, `forum`, `social`, `Pinterest board`, `tool`, `local business`, `news`, `dictionary` | `youtube.com/watch...` is `other: video`; `pinterest.com/ideas/...` is `other: Pinterest board`; `reddit.com/...` is `other: forum` |

Write `other` with a colon and the specific kind; a bare `other` fails the
count script.

## serp-intent.md format

Save as `briefs/[slug]/serp-intent.md`. Copy URLs and titles exactly from the
response; escape a `|` inside a title as `\|`.

```markdown
# SERP intent: [focus keyword]

- Focus keyword: [focus keyword]
- Location / language: United States / English (location_code 2840, language_code en)
- Checked: [YYYY-MM-DD]
- Endpoint: POST /v3/serp/google/organic/live/advanced (mcp__dataforseo__api_request, noAiMode true)
- Cost: $[cost from response]

## Top 10 organic results

Organic results on page 1: [N]

| Rank | URL | Title | Page type |
|---|---|---|---|
| 1 | [url] | [title] | [page type] |

## Page type counts

## AI Overview

Present: [yes/no]

## People Also Ask

- [question, verbatim]

## Related searches

- [search, verbatim]

## Intent conclusion

[One sentence: the core intent page type and what the searcher wants.]
```

- Leave `## Page type counts` empty; `scripts/count_serp_types.py` fills it.
- When the SERP has no People Also Ask or related searches, write
  `None on this SERP.` under that heading.
- If the user switches keyword after a stop, overwrite this file for the new
  keyword.
