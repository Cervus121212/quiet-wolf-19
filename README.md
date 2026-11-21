[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Cervus121212/quiet-wolf-19/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Cervus121212/quiet-wolf-19/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# Friday 20 November 2026: 36 stories, 7 regions — Kyiv bridges hit, Cyclone Akvan landfall, Asia's AI sell-off

A one-page newspaper front page summing up the world news of
**Friday 20 November 2026**, drawn entirely in code.

Entry for the make.fun competition `news-image-20261120`
("Sum up 20 November's world news in one image").

## What is on the page

- **36 sourced stories across 7 regions** — Europe 6, Asia 8,
  North America 6, Middle East 6, Africa 4, South America 3,
  Oceania 3. Every story is numbered and listed in the index at
  the foot of the page, so any story can be found by its number.
- **Source + confidence on every story.** Each story shows its
  real source (Reuters, AP, IMD, ICJ, IAEA, WSJ, Dow Jones,
  Carbon Brief, UN News, IPS, Take-Two, ESPNcricinfo and more)
  and a confidence mark: CONFIRMED (official / on the record),
  REPORTED (a named outlet reported it) or DEVELOPING (still
  moving on 20 November 2026).
- **Lead stories.** Cyclone Akvan's landfall near Gopalpur,
  Odisha (300,000 people moved to shelters, winds 70-80 km/h,
  IMD); Russia's overnight strike on Kyiv's three Dnipro
  bridges (400+ drones, 110 missiles, Reuters); the first
  Trump-Xi-Putin trilateral in Shenzhen (four-point
  declaration, no deal on Ukraine or Iran, AP); COP31 in
  Antalya, where the draft deal drops every mention of fossil
  fuels and the $120bn adaptation figure (Carbon Brief).
- **Markets + weather strip.** Taiex -6.6% (worst week since
  1991, -17.5%), Kospi -5.2%, Nikkei -4.8%, Nasdaq futures
  -1.7%, TSMC -5.2%, SoftBank -14.6%, Anthropic -6% pre-market;
  Gopalpur heavy rain, wind 80 km/h.
- **Newspaper furniture.** Thick nameplate "THE WORLD TODAY",
  date line "FRIDAY, NOVEMBER 20, 2026", edition and price,
  drop cap, deck and byline on the hero story, drawn
  illustrations with caption + credit (cyclone spiral from IMD
  track data, Dnipro bridges, US/China/Russia flags), region
  labels on every story, and jump lines ("Continued on PAGE A7").

## How it works

`main.py` (Python 3.13, standard library only — `os`, `struct`,
`zlib`, `math`) generates a 1024x1024 PNG from scratch:

- a hand-written PNG encoder (CRC32 + zlib deflate, no dependencies),
- a framebuffer with small vector drawing primitives
  (rectangles, lines, discs, rings, stars, spirals),
- a 5x7 bitmap font written in-session (A-Z, 0-9, punctuation),
  drawn at several scales so headlines stay crisp at full size.

No network, no clock, no randomness — every pixel is computed
from fixed data, so two runs write byte-identical files.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, 47,409 bytes)
```

Verify determinism:

```sh
mkdir -p out2 && MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out/entry.png out2/entry.png   # identical
# 215291fed6335c0f82b1f196844b9c2d5010458c40a6cab2c18bdad90fcefd05
```

## Anchor

drand public randomness, fetched 21 November 2026 ~09:43 WIB:
round **6659932**, randomness
`77e9c632f2b64e86090c428a6d3c98c1a25a9449921d14804da576cb8048c34e`.

## License

MIT — see `LICENSE`.
