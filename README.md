<div align="center">

# mpc-rpc

Event-based Discord Rich Presence integration for MPC-HC.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)](https://python.org)
[![Discord](https://img.shields.io/badge/Discord-Rich%20Presence-5865F2?logo=discord&logoColor=white)](https://discord.com)
[![MPC-HC](https://img.shields.io/badge/MPC--HC-compatible-red)](https://github.com/clsid2/mpc-hc)

<img src="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/s_movie.png" width="32%" />
<img src="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/s_movie2.png" width="32%" />
<img src="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/s_series.png" width="32%" />

</div>

## Requirements

- [MPC-HC](https://github.com/clsid2/mpc-hc) with Web Interface enabled (`View → Options → Web Interface → Listen on port`)

## Usage

```
mpc-rpc.exe -a <adapter> [options]
```

### Options

| Flag | Description | Default |
|---|---|---|
| `-p`, `--port` | MPC-HC Web Interface port | `13579` |
| `-a`, `--adapter` | Source adapter for media metadata | required |
| `--token` | API token (required for some adapters) | — |

### Example

```bash
# Using IMDB
mpc-rpc.exe --adapter imdb

# Using TMDB (requires API token)
mpc-rpc.exe --adapter tmdb --token YOUR_TOKEN

# Custom port
mpc-rpc.exe --adapter imdb --port 13580
```

## Adapters

| Adapter | Token required | Description |
|---|---|---|
| `imdb` | No | Fetches media metadata from IMDB |
| `tmdb` | Yes | Fetches media metadata from [The Movie Database](https://www.themoviedb.org/settings/api) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md).
