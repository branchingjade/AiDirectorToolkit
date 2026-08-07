# MovieStillsDB Film Slug Patterns

Quick reference for film slug naming conventions used in CDN URLs.

## Confirmed Slugs (verified this session)

| Film | Year | Slug | Still Count |
|------|------|------|-------------|
| Room | 2015 | `room` | 21 |
| The Silence of the Lambs | 1991 | `the-silence-of-the-lambs` | 218 |
| You (Netflix) | 2018 | `you` | 609 |
| Barbarian | 2022 | `barbarian` | 7 |
| 10 Cloverfield Lane | 2016 | `10-cloverfield-lane` | 59 |
| Dogtooth | 2009 | `dogtooth` | 15 |
| Misery | 1990 | `misery` | 82 |
| Berlin Syndrome | 2017 | `berlin-syndrome` | 140 |

## Slug Naming Rules

- All lowercase
- Spaces → hyphens
- Articles ("the", "a") included when part of official title
- Year not in slug (year shown separately on site)
- TV shows in quotes on site but slug has no quotes
- Colons/special chars → hyphens or omitted

## Examples of Other Patterns

- `the-silence-of-the-lambs` (includes "the")
- `10-cloverfield-lane` (number preserved)
- `berlin-syndrome` (two words, hyphenated)
- `you` (single word, no qualifier for Netflix series)
