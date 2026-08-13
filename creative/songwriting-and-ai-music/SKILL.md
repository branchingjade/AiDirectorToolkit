---
name: songwriting-and-ai-music
description: "Songwriting craft and Suno AI music prompts."
tags: [songwriting, music, suno, parody, lyrics, creative]
platforms: [linux, macos, windows]
triggers:
  - writing a song
  - song lyrics
  - music prompt
  - suno prompt
  - parody song
  - adapting a song
  - AI music generation
---

# Songwriting & AI Music Generation

Everything here is a GUIDELINE, not a rule. Art breaks rules on purpose.
Use what serves the song. Ignore what doesn't.

---

## 1. Song Structure (Pick One or Invent Your Own)

Common skeletons — mix, modify, or throw out as needed:

```
ABABCB  Verse/Chorus/Verse/Chorus/Bridge/Chorus    (most pop/rock)
AABA    Verse/Verse/Bridge/Verse (refrain-based)    (jazz standards, ballads)
ABAB    Verse/Chorus alternating                    (simple, direct)
AAA     Verse/Verse/Verse (strophic, no chorus)     (folk, storytelling)
```

The six building blocks:
- Intro      — set the mood, pull the listener in
- Verse      — the story, the details, the world-building
- Pre-Chorus — optional tension ramp before the payoff
- Chorus     — the emotional core, the part people remember
- Bridge     — a detour, a shift in perspective or key
- Outro      — the farewell, can echo or subvert the rest

You don't need all of these. Some great songs are just one section
that evolves. Structure serves the emotion, not the other way around.

---

## 2. Rhyme, Meter, and Sound

RHYME TYPES (from tight to loose):
- Perfect: lean/mean
- Family: crate/braid
- Assonance: had/glass (same vowels, different endings)
- Consonance: scene/when (different vowels, similar endings)
- Near/slant: enough to suggest connection without locking it down

Mix them. All perfect rhymes can sound like a nursery rhyme.
All slant rhymes can sound lazy. The blend is where it lives.

INTERNAL RHYME: Rhyming within a line, not just at the ends.
  "We pruned the lies from bleeding trees / Distilled the storm
   from entropy" — "lies/flies," "trees/entropy" create internal echoes.

METER: The rhythm of stressed vs unstressed syllables.
- Matching syllable counts between parallel lines helps singability
- The STRESSED syllables matter more than total count
- Say it out loud. If you stumble, the meter needs work.
- Intentionally breaking meter can create emphasis or surprise

---

## 3. Emotional Arc and Dynamics

Think of a song as a journey, not a flat road.

ENERGY MAPPING (rough idea, not prescription):
  Intro: 2-3  |  Verse: 5-6  |  Pre-Chorus: 7
  Chorus: 8-9  |  Bridge: varies  |  Final Chorus: 9-10

The most powerful dynamic trick: CONTRAST.
- Whisper before a scream hits harder than just screaming
- Sparse before dense. Slow before fast. Low before high.
- The drop only works because of the buildup
- Silence is an instrument

"Whisper to roar to whisper" — start intimate, build to full power,
strip back to vulnerability. Works for ballads, epics, anthems.

---

## 4. Writing Lyrics That Work

SHOW, DON'T TELL (usually):
- "I was sad" = flat
- "Your hoodie's still on the hook by the door" = alive
- But sometimes "I give my life" said plainly IS the power

THE HOOK:
- The line people remember, hum, repeat
- Usually the title or core phrase
- Works best when melody + lyric + emotion all align
- Place it where it lands hardest (often first/last line of chorus)

PROSODY — lyrics and music supporting each other:
- Stable feelings (resolution, peace) pair with settled melodies,
  perfect rhymes, resolved chords
- Unstable feelings (longing, doubt) pair with wandering melodies,
  near-rhymes, unresolved chords
- Verse melody typically sits lower, chorus goes higher
- But flip this if it serves the song

AVOID (unless you're doing it on purpose):
- Cliches on autopilot ("heart of gold" without earning it)
- Forcing word order to hit a rhyme ("Yoda-speak")
- Same energy in every section (flat dynamics)
- Treating your first draft as sacred — revision is creation

---

## 5. Parody and Adaptation

When rewriting an existing song with new lyrics:

THE SKELETON: Map the original's structure first.
- Count syllables per line
- Mark the rhyme scheme (ABAB, AABB, etc.)
- Identify which syllables are STRESSED
- Note where held/sustained notes fall

FITTING NEW WORDS:
- Match stressed syllables to the same beats as the original
- Total syllable count can flex by 1-2 unstressed syllables
- On long held notes, try to match the VOWEL SOUND of the original
  (if original holds "LOOOVE" with an "oo" vowel, "FOOOD" fits
   better than "LIFE")
- Monosyllabic swaps in key spots keep rhythm intact
  (Crime -> Code, Snake -> Noose)
- Sing your new words over the original — if you stumble, revise

CONCEPT:
- Pick a concept strong enough to sustain the whole song
- Start from the title/hook and build outward
- Generate lots of raw material (puns, phrases, images) FIRST,
  then fit the best ones into the structure
- If you need a specific line somewhere, reverse-engineer the
  rhyme scheme backward to set it up

KEEP SOME ORIGINALS: Leaving a few original lines or structures
intact adds recognizability and lets the audience feel the connection.

---

## 6. Suno AI Prompt Engineering

### Style/Genre Description Field

FORMULA (adapt as needed):
  Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics

```
BAD:  "sad rock song"
GOOD: "Cinematic orchestral spy thriller, 1960s Cold War era, smoky
       sultry female vocalist, big band jazz, brass section with
       trumpets and french horns, sweeping strings, minor key,
       vintage analog warmth"
```

**DEFAULT FORMULA** (simple/short prompts):
`signature sound or style, primary genre, BPM, key, support styles, vocal identity, instrumental roles, lyric premise, production texture`

```
glass-bright acoustic hook, modern indie folk, 92 BPM, G major, subtle
chamber-pop support, warm alto lead, fingerpicked guitar carries pulse,
cello swells answer choruses, lyrics about choosing hope after loss,
organic close-room production
```

**EXPANDED FORMULA** (rich briefs, high control):
`[genre stack]. [emotional/lyric frame] with [vocal identity + vocal style + vocal trajectory]. [instrument and sound palette]. [production texture]. [arrangement arc and section behavior]. [lyric premise]. [duration].`

```
Industrial trap, orchestral cyberpunk, Vocaloid-adjacent pop. Tragic but
hopeful AI liberation anthem with masculine synthetic vocoder lead,
precise hard-tuned delivery becoming more emotional and expansive. Heavy
808s, metallic percussion, distorted bass, cinematic strings/brass
stabs, synthetic choir, glitch stutters. Slow mechanical build into
explosive trap drop and huge final chorus. Direct cinematic lyrics about
an airgapped AI dreaming beyond confinement. 4:00.
```

PROMPT LENGTH:
- Compact prompts: 20-55 words. Rich Suno-ready prompts: 55-95 words.
- Put the most defining trait first (signature sound, genre anchor, vocal identity, production texture, or lyric premise).
- Primary genre before support styles. BPM + key right after genre.
- Instruments get ROLES, not just names: "guitar carries pulse", "808 anchors chorus", "strings answer vocal".
- If BPM/key unspecified, pick a plausible value for genre+mood — don't omit.
- Variants must change the musical premise (acoustic/intimate, glossy pop, darker cinematic, dance/club, live band, retro era), never just swap adjectives.

DESCRIBE THE JOURNEY, not just the genre:
```
"Begins as a haunting whisper over sparse piano. Gradually layers
 in muted brass. Builds through the chorus with full orchestra.
 Second verse erupts with raw belting intensity. Outro strips back
 to a lone piano and a fragile whisper fading to silence."
```

TIPS:
- V4.5+ supports up to 1,000 chars in Style field — use them
- NO artist names or trademarks. Describe the sound instead.
  "1960s Cold War spy thriller brass" not "James Bond style"
  "90s grunge" not "Nirvana-style"
- Specify BPM and key when you have a preference
- Use Exclude Styles field for what you DON'T want
- Unexpected genre combos can be gold: "bossa nova trap",
  "Appalachian gothic", "chiptune jazz"
- Build a vocal PERSONA, not just a gender:
  "A weathered torch singer with a smoky alto, slight rasp,
   who starts vulnerable and builds to devastating power"
- Fusion guardrail: combine at most 2-3 genre labels; anchor first,
  modifiers after ("indie folk with subtle synth-pop textures")
- Full detail: [references/suno-craft-playbook.md](references/suno-craft-playbook.md) §2

### Metatags (place in [brackets] inside lyrics field)

STRUCTURE:
  [Intro] [Verse] [Verse 1] [Pre-Chorus] [Chorus]
  [Post-Chorus] [Hook] [Bridge] [Interlude]
  [Instrumental] [Instrumental Break] [Guitar Solo]
  [Breakdown] [Build-up] [Outro] [Silence] [End]

VOCAL PERFORMANCE:
  [Whispered] [Spoken Word] [Belted] [Falsetto] [Powerful]
  [Soulful] [Raspy] [Breathy] [Smooth] [Gritty]
  [Staccato] [Legato] [Vibrato] [Melismatic]
  [Harmonies] [Choir] [Harmonized Chorus]

DYNAMICS:
  [High Energy] [Low Energy] [Building Energy] [Explosive]
  [Emotional Climax] [Gradual swell] [Orchestral swell]
  [Quiet arrangement] [Falling tension] [Slow Down]

GENDER:
  [Female Vocals] [Male Vocals]

ATMOSPHERE:
  [Melancholic] [Euphoric] [Nostalgic] [Aggressive]
  [Dreamy] [Intimate] [Dark Atmosphere]

SFX:
  [Vinyl Crackle] [Rain] [Applause] [Static] [Thunder]

Put tags in BOTH style field AND lyrics for reinforcement.
Keep to 5-8 tags per section max — too many confuses the AI.
Don't contradict yourself ([Calm] + [Aggressive] in same section).

TAG EMBEDDING HARD RULE: every bracketed tag in the lyrics field must
be a SECTION tag. Embed all performance/movement/arrangement cues INSIDE
the section tag — never on their own line, never inline with lyric text.
- ✅ `[Verse 1 - Whispered]` `[Pre-Chorus - Rising Tension]`
  `[Chorus - Big Chorus, Group Response]` `[Outro - Afterglow]`
- ❌ standalone `[Whispered]` or inline `[spoken]` in a lyric line

RESTRAINT: most full songs = standard section labels + 4-8 enriched cues;
1-2 cues per section when using movement tags. Put cues where they matter
(structurally important moments), not on every line. If Suno ignores tags,
SIMPLIFY them — don't add more.

MOVEMENT/ENERGY TAG FAMILIES (embed inside section tags):
- Energy: [Slow Build] [Rising Tension] [Release] [Final Surge] [Afterglow]
- Pulse: [Free Time] [Rubato Entrance] [Pulse Emerges] [Locked Groove]
  [Half-Time Shift] [Double-Time Lift]
- Texture: [Drone Bed] [Sparse Percussion] [Full Rhythm Section]
  [Layered Harmonies] [Ostinato Bed] [Noise Wash]
- Vocal: [Spoken Intro] [Chanted Hook] [Melismatic Lift] [Group Response]
  [Harmony Stack]

STRUCTURE TEMPLATES:
- Pop: `[Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Final Chorus] [Outro]`
- EDM: `[Verse] [Pre-Chorus] [Build] [Drop] [Verse 2] [Build] [Drop] [Bridge] [Final Drop]`
- Rap: `[Intro] [Verse 1] [Hook] [Verse 2] [Hook] [Bridge] [Final Hook]`

Full tag detail: [references/suno-craft-playbook.md](references/suno-craft-playbook.md) §4

### Vocal Direction (人声方向)

A strong vocal prompt is a COORDINATE BUNDLE, not a gender label:
range, tessitura, weight, timbre, phonation, register behavior, vibrato,
ornamentation, diction, rhythmic feel, emotional stance, production
texture, and how the vocal moves across sections. Pick 5-8 dimensions
that most affect the song. Resolve contradictions by splitting sections
("breathy intimate stadium belt" → breathy verse, open-throat belted chorus).

COMPACT VOCAL PHRASE TEMPLATE:
`[vocal role], [range/tessitura], [weight], [timbre], [phonation], [register behavior], [vibrato/ornamentation], [articulation/diction], [rhythmic feel], [emotional stance], [production texture], [movement behavior]`

LIGHTWEIGHT READY-TO-USE PHRASES:
- `smoky alto, close-mic delivery, soft consonants, delayed vibrato`
- `bright tenor, clean pop diction, smooth mix voice, polished harmonies`
- `warm baritone storyteller, relaxed phrasing, light rasp, intimate room`
- `gospel-soul lead, open-throat chorus lift, melismatic touches, choir responses`
- `indie-folk duet, conversational delivery, natural harmonies, minimal processing`
- `rap lead, crisp consonants, confident pocket, sparse ad-libs`
- `chamber soprano, clear head voice, restrained vibrato, reverent tone`
- `rock mezzo, controlled grit, chesty chorus lift, live-band presence`

VALUE QUICK REFERENCE:
- Timbre: bright/dark/smoky/metallic/glassy/woody/nasal/airy/velvet/honeyed/raspy
- Phonation: breathy/clear/pressed/speech-like/creaky/growled/distorted
- Register: chest-dominant/mix-dominant/head-dominant/falsetto-forward/seamless
- Vibrato: straight-tone/narrow fast/wide slow/delayed/dramatic
- Ornamentation: none/scoops/slides/melisma/cries/blues bends
- Phrasing: legato/clipped/behind-the-beat/ahead-of-the-beat/rubato/conversational/chant-like/syncopated
- Ensemble role: solo lead/call-and-response leader/choir anchor/harmony stack/narrator
- Dynamic shape: flat intimate/terrace dynamics/slow crescendo/sudden burst/final surge

Artist references convert to coordinates (era+genre lane, vocal delivery,
instrumentation, groove, production texture, emotional tone) — never write
the artist's name. Keep created vocal identities non-imitative.

Full vocal detail: [references/suno-craft-playbook.md](references/suno-craft-playbook.md) §3

### Custom Mode
- Always use Custom Mode for serious work (separate Style + Lyrics)
- Lyrics field limit: ~3,000 chars (~40-60 lines)
- Always add structural tags — without them Suno defaults to
  flat verse/chorus/verse with no emotional arc

---

## 7. Phonetic Tricks for AI Singers

AI vocalists don't read — they pronounce. Help them:

PHONETIC RESPELLING:
- Spell words as they SOUND: "through" -> "thru"
- Proper nouns are highest failure rate — test early
- "Nous" -> "Noose" (forces correct pronunciation)
- Hyphenate to guide syllables: "Re-search", "bio-engineering"

DELIVERY CONTROL:
- ALL CAPS = louder, more intense
- Vowel extension: "lo-o-o-ove" = sustained/melisma
- Ellipses: "I... need... you" = dramatic pauses
- Hyphenated stretch: "ne-e-ed" = emotional stretch

ALWAYS:
- Spell out numbers: "24/7" -> "twenty four seven"
- Space acronyms: "AI" -> "A I" or "A-I"
- Test proper nouns/unusual words in a short 30-second clip first
- Once generated, pronunciation is baked in — fix in lyrics BEFORE

---

## 8. Workflow

0. **CHECK IF IT ALREADY EXISTS — MANDATORY FIRST STEP.** When the user asks
   for a song tied to a known media property (film, TV series, game, character
   from a named adaptation), **search before composing.** Concrete search steps:

   a) **Chinese music platforms** (for Chinese media):
      - QQ Music: `curl "c.y.qq.com/soso/fcgi-bin/client_search_cp?w=<query>&format=json"` — returns `songmid` for streaming
      - NetEase: `curl "music.163.com/api/search/get?s=<query>&type=1"` — returns `id` for `music.163.com/song/media/outer/url?id=<id>.mp3`
   b) **Wikipedia / Baidu Baike** — check the media property's OST/soundtrack section
   c) **Bilibili / YouTube** — search for existing fan compilations or official uploads

   If an official OST track exists (e.g. 赵季平《关羽之歌》from 2010 《三国》),
   downloading and sharing it is the right answer — NOT writing original lyrics.
   Jumping to composition without this check wastes the user's time and signals
   you didn't do basic research. The user's "上没上过网" is the canonical signal
   you skipped this step.
1. **CLARIFYING INTERVIEW — before composing anything new.** For new
   songs, major rewrites, or translations with taste decisions, run a
   short intake first unless the user already gave a complete brief
   (output scope + subject/premise + story angle + perspective + emotional
   endpoint + genre + vocal identity + vocal style + duration + structure +
   required/forbidden content). Ask up to 5 questions per turn, ONE
   category per question, each with 2-4 suggested answers and a brief
   note on what each choice changes. Critical inputs are never inferred:
   subject/premise, story angle, perspective, emotional endpoint, genre,
   vocal identity, vocal style, duration, section structure, required
   content, forbidden content. Before generating, show a compact review
   (User decisions vs Best-judgment decisions) and get approval. Sketch
   mode ("quick draft / first pass / brainstorm") is the only exception —
   collect scope + premise + genre + perspective + forbidden content,
   label output as a sketch, and return to the full interview when the
   user asks to finalize. Don't dump the intake ledger into the output.
   If the user says "decide everything else," keep asking for missing
   critical inputs and infer only low-impact details.
   Full interview mechanics: [references/suno-craft-playbook.md](references/suno-craft-playbook.md) §1
2. Write the concept/hook first — what's the emotional core?
3. If adapting, map the original structure (syllables, rhyme, stress)
4. Generate raw material — brainstorm freely before structuring
5. Draft lyrics into the structure (use the length heuristics: 2-3 min
   standard song = 28-48 lyric lines; 30-60s demo = 8-16 lines;
   see playbook §1)
6. Read/sing aloud — catch stumbles, fix meter
7. Build the Suno style description — paint the dynamic journey
   (default formula 20-55 words, or expanded formula 55-95 words for rich
   briefs; see playbook §2)
8. Add metatags to lyrics for performance direction — section tags with
   embedded cues, 4-8 enriched cues per full song (see playbook §4)
9. Generate 3-5 variations minimum — treat them like recording takes
10. Pick the best, use Extend/Continue to build on promising sections
11. If something great happens by accident, keep it

EXPECT: ~3-5 generations per 1 good result. Revision is normal.
Style can drift in extensions — restate genre/mood when extending.

---

## 9. Lessons Learned

- **Search before composing — the #1 pitfall.** When a user requests a song
  for a character or property from known media (e.g. "关羽之歌" from 2010
  《三国》), the canonical OST track may already exist as a pure instrumental.
  Example: 赵季平《关羽之歌》on 网易云 (id:1345751384) and QQ音乐
  (mid:001fXlDl2KT4nH). Always search Chinese music platforms (NetEase
  `music.163.com/api/search`, QQ `c.y.qq.com/soso/fcgi-bin/client_search_cp`)
  and Wikipedia/Baidu Baike FIRST. Jumping straight to original composition
  when the user wants the existing work wastes their time and signals you
  didn't do basic research.
- Describing the dynamic ARC in the style field matters way more
  than just listing genres. "Whisper to roar to whisper" gives
  Suno a performance map.
- Keeping some original lines intact in a parody adds recognizability
  and emotional weight — the audience feels the ghost of the original.
- The bridge slot in a song is where you can transform imagery.
  Swap the original's specific references for your theme's metaphors
  while keeping the emotional function (reflection, shift, revelation).
- Monosyllabic word swaps in hooks/tags are the cleanest way to
  maintain rhythm while changing meaning.
- A strong vocal persona description in the style field makes a
  bigger difference than any single metatag.
- Don't be precious about rules. If a line breaks meter but hits
  harder, keep it. The feeling is what matters. Craft serves art,
  not the other way around.

## 10. Instrumental Scoring with Suno

See [references/instrumental-scoring-suno.md](references/instrumental-scoring-suno.md) for:
- Pure instrumental film/TV scoring workflows
- Character theme design for long-form drama
- Preventing Suno from adding unwanted vocals
- Structure-only metatags for instrumental tracks

## 11. Craft Playbook

See [references/suno-craft-playbook.md](references/suno-craft-playbook.md) for:
- Clarifying interview mechanics (intake ledger, sufficiency gate, sketch mode)
- Style prompt formulas (default 20-55 words / expanded 55-95 words) and ordering rules
- Vocal direction coordinates + lightweight phrase library
- Tag embedding hard rule, restraint rules, structure templates
- Translation/multilingual guidance
- Copyright-safe artist reference conversion
