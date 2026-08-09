# PayQuant 3D Quantum Diamond Exploration

![PayQuant Quantum](https://img.shields.io/badge/PayQuant-Quantum-2.0-bright?style=for-the-badge)

**Every block mints a unique 3D diamond-like structure** — a publicly
verifiable geometric signature derived from the block's quantum footprint.

## How the Quantum Diamond is built

```
TRNG seed (desktop only) ─▶ 8-qubit quantum simulator (panta-sim)
                                 │
                      most probable outcome
                                 │
       SHA-256(prev_hash|outcome|miner|seed)  =  footprint (public)
                                 │
        ┌──────────────┬─────────┴──────────┬──────────────┐
        ▼              ▼                    ▼              ▼
   3D geometry    dynamic lighting     color palette   refraction/
   (vertices,    (primary, secondary,   from facets     sparkle
      faces)       ambient)                             effects
```

- The **footprint** is a 64-hex SHA-256 digest — public and attack-resistant.
- The **3D diamond** (vertices / faces / lighting / colors) is derived **only
  from the public footprint**, so any node can reproduce it without the seed.
- The **TRNG seed** is used once at mint time and never stored in a block or
  committed to the repository.

## The mainnet genesis diamond

Block **0** of the mainnet is shown first in the gallery. Its diamond is derived
from the canonical public genesis record in `contrib/chain_db.py`
(`GENESIS_BLOCK`) — same geometry, lighting and colors every node and every
re-render produces. Chain-start constants are listed in `README.md`.

## Exploring the diamonds

### 1. Local file explorer (`explorer_3d/`)
```bash
python tools/build_gallery3d.py       # regenerates diamonds.json (public headers)
cd explorer_3d && python -m http.server 8000
# open http://localhost:8000
```
- Rotate / zoom with the mouse or touch; auto-rotation is on by default.
- **◈ Gallery** shows up to 400 block diamonds.
- **Next ▸ / ◂ Prev** switch blocks; the panel shows the public footprint.

### 2. GitHub Pages (public deployment)
The autonomous build pushes the public gallery to the site, published at:
`https://timfromhcs.github.io/payquant/explorer/3d`

## Security guarantees

- Diamonds are generated from **public** data only.
- No private keys, seeds, or wallet data are ever encoded in the geometry,
  lighting, or payloads.
- The validator (`contrib/pqn_quantum/footprints.py`) re-mints a footprint from
  the same seed + header and requires an exact match — forging a diamond
  requires a SHA-256 collision.

## Performance targets

| Stage | Target |
| --- | --- |
| Footprint + geometry generation | < 100 ms |
| Block validation | < 30 ms |
| 3D render (WebGL) | 60 fps |

## Public vs desktop-only

| Public (safe in repo) | Desktop-only (never committed) |
| --- | --- |
| footprint hash | TRNG seed |
| 3D geometry / lighting / colors | private keys |
| block headers & TX summaries | wallet database |
| miner public addresses | UTXO cache |

Made with love by timfromhcs & hcsmedia — all secrets remain local.