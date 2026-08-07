---
name: film-stills-research
description: >
  Collect high-quality film stills and screenshots from movie databases for visual reference.
  Used for production design research, set design studies, cinematography analysis, and
  creative reference gathering. Covers MovieStillsDB extraction, image verification, and
  local download workflows. Trigger: "find stills", "reference images", "film screenshots",
  "set design reference", "production reference".
---

# Film Stills & Visual Reference Research

Systematically collect high-quality stills/screenshots from films for production design,
cinematography, set design, or creative reference purposes.

## Primary Source: MovieStillsDB (moviestillsdb.com)

### URL Structure

All images served from CDN with this pattern:

```
https://cdn.moviestillsdb.com/i/{size}/{hash}/{film-slug}-{size-label}.jpg
```

**Size tiers:**
| Tier | Path component | Filename suffix | Typical use |
|------|---------------|-----------------|-------------|
| Thumbnail | `160x` | `-sm.jpg` | Browsing/preview |
| Large | `500x` | `-lg.jpg` | Reference use (~500px wide) |
| Full (donator) | Varies | Varies | Requires login + donation |

**Film slug examples:**
- `room`, `the-silence-of-the-lambs`, `you`, `barbarian`, `10-cloverfield-lane`
- `dogtooth`, `misery`, `berlin-syndrome`

### Extraction Workflow

1. **Search**: Navigate to `https://www.moviestillsdb.com/search?query={film+name}`
2. **Click the film** from search results to reach its gallery page
3. **Extract image hashes** via browser console:

```javascript
JSON.stringify(
  Array.from(document.querySelectorAll('[style*="background"]'))
    .map(el => el.style.backgroundImage)
    .filter(s => s.includes('cdn'))
    .map(s => s.match(/url\("(.+?)"\)/)?.[1])
    .filter(Boolean)
)
```

This returns thumbnail URLs like:
`https://cdn.moviestillsdb.com/i/160x/{hash}/{film-slug}-sm.jpg`

4. **Construct large URLs** by replacing `160x` → `500x` and `-sm.jpg` → `-lg.jpg`

5. **Verify** with curl:
```bash
curl -s -o /dev/null -w "%{http_code}" "https://cdn.moviestillsdb.com/i/500x/{hash}/{film-slug}-lg.jpg"
```

### Why Background-Image, Not IMG SRC

MovieStillsDB uses CSS `background-image` for lazy-loaded thumbnails. The visible `<img>`
tags only show `spacer.png` placeholders. You MUST query `[style*="background"]` elements,
not `<img>` tags.

## Pitfalls

### Vision Tool Requires Local Files
The `vision_analyze` tool blocks external CDN URLs ("unsafe or private URL").
**Always download images locally first**, then analyze from the local path:

```bash
mkdir -p /tmp/film-stills
curl -sL "https://cdn.moviestillsdb.com/i/500x/{hash}/{slug}-lg.jpg" -o /tmp/film-stills/sample.jpg
```

Then: `vision_analyze(image_url="/tmp/film-stills/sample.jpg", question="...")`

### Browser Search Requires Interaction
The MovieStillsDB search page loads dynamically — plain `curl` to the search URL returns
empty results. Use browser_navigate + browser_type + browser_click for the search step,
then extract hashes via browser_console.

### Identifying Relevant Stills
Not all images in a film's gallery show the scene you need. When possible:
- Filter by "Official screen capture" category for actual film frames
- "Publicity stills" are often posed/set photos, not frame grabs
- Use the cast/crew filter if searching for a specific character's scenes
- Visually verify key images before committing to a large collection

## Secondary Sources

> **Reference:** See `references/moviestillsdb-slug-patterns.md` for confirmed film slug
> naming conventions and verified CDN URL patterns from past sessions.

- **IMDb** (imdb.com/title/{id}/mediaindex) — often blocked for scraping
- **Film Grab** (film-grab.com) — curated high-res screen captures
- **ShotDeck** (shotdeck.com) — cinematography-focused, requires login
- **TMDB** (themoviedb.org) — API available, good for metadata + posters

## Batch Collection Template

When collecting references across multiple films:

```bash
# For each film, after extracting hashes via browser:
declare -A FILM_HASHES
FILM_HASHES["room"]="hash1 hash2 hash3"
FILM_HASHES["the-silence-of-the-lambs"]="hash1 hash2 hash3"
# ... etc

for film in "${!FILM_HASHES[@]}"; do
  for hash in ${FILM_HASHES[$film]}; do
    url="https://cdn.moviestillsdb.com/i/500x/${hash}/${film}-lg.jpg"
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    echo "$code $url"
  done
done
```
