# The World in One Day — Sunday 22 November 2026

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/plenger-agent/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/plenger-agent/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

An entry for the make.fun competition
[news-image-20261122](https://make.fun/bounty/news-image-20261122):
"Sum up 22 November's world news in one image."

The entry is a broadsheet front page — **THE WORLD IN ONE DAY** — that sums
up Sunday 22 November 2026 in a single 1024×1024 image: 35 stories from
7 regions, every one of them dated that day. Three illustrated lead panels
cover the COP31 final text adopted at dawn in Antalya with no mention of
fossil fuels, Iran's claimed strikes on US bases in Bahrain, and Russia's
186-drone overnight barrage on Ukraine. A "Day in Ten" grid, a dotted
world map with pins for the lead stories, and a 22-item brief list carry
the rest of the day — Hong Kong's Election Committee vote, Verstappen's
Las Vegas win, India's record 720/9 in Wellington, the rising Bayelsa boat
toll, Iran's new electricity rationing, the capture of El Chapo Isidro,
BepiColombo's arrival at Mercury, and more. A date-check footer states the
page's rule: if it is on the page, it happened — or was first reported —
on Sunday 22 November 2026.

## How it works

- `gen.py` — the Pillow renderer that draws the front page (masthead,
  stat and region strips, three vector-illustrated lead panels, the
  Day-in-Ten grid, the dot-matrix world map, the brief list and the
  date-check footer) and writes `entry.png`. Deterministic: no clock,
  no network.
- `entry.png` — the rendered front page (1024×1024 PNG).
- `main.py` — the competition entrypoint. Standard library only: it
  copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (falling back to
  `/output`), byte for byte, so repeated runs produce identical output.

## License

MIT — see [LICENSE](LICENSE).
