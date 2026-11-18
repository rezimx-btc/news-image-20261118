# The World in One Day — news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/rezimx-btc/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/rezimx-btc/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

[View the bounty on make.fun](https://make.fun/bounty/news-image-20261118)

A one-page newspaper of the world on **Wednesday 18 November 2026**,
drawn entirely by a stdlib-only Python script (`main.py`, no Pillow, no
network). It renders a 1024x1024 PNG: masthead and date, a lead story on
the U.S. strike on an Iranian missile site on Qeshm Island with a Gulf
schematic, a numbered world map, a seven-story grid plus an in-brief box,
a markets strip (18 Nov closes), and a footer.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (24,156 bytes). Deterministic: two runs produce
byte-identical output (sha256
`c1896dddd8d1361c41f2d6de9300410c5dcadbcb7205dea5236986e2e538c34e`).

## Stories (all reported on 18 November 2026)

1. U.S. strikes Iranian missile site on Qeshm Island; Iran fires drones
   at Bahrain and Kuwait.
2. Ukraine hits the Kerch Bridge to Crimea a second day; part of the
   road span collapses.
3. Xi, Putin and Trump meet in Shenzhen this week.
4. Democrat Mary Peltola wins the Alaska Senate seat; Democrats take
   56 seats.
5. Ebola in DR Congo more than doubles: 11,000+ cases, 5,400 deaths.
6. The U.S. loses measles-free status after 26 years: 5,400+ cases,
   10 deaths.
7. A Russian military plane crashes in Siberia (Kemerovo), 19 dead.
8. Cold kills in Gaza tents as Australia, Canada, Italy and the UK call
   on Israel to let aid reach flooded Gaza.

In brief: 6.0 quake in Papua New Guinea; Category 5 Cyclone Xavier hits
the Northern Cook Islands; Waymo pulls driverless taxis from U.S.
freeways; Herzog taps Eisenkot to form an Israeli government; France's
fourth weekend of cost-of-living protests.

Markets (18 Nov close): CAC 40 8,216.78 -1.62%, DAX 26,045.37 -2.08%,
FTSE 100 -1.76%, S&P 500 7,340.53 -1.03%, Nasdaq 24,328.38 -0.74%,
Nikkei 225 59,024.28 +0.20%.

## License

MIT — see `LICENSE`.
