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
mpc-rpc.exe
```

## Default Configuration

```toml
[mpc]
port = 13579

[adapter]
name = "imdb"
# name = "tmdb"
# token = "your_token_here"
# ...

[uploader]
name = "litterbox"
# name = "imgbb"
# token = "your_token_here"
# ...
```

## Adapters

| Adapter | Token required | Description |
|---|---|---|
| `imdb` | No | Fetches media metadata from [IMDB](https://www.imdb.com) |
| `mal` | No | Fetches media metadata from [MyAnimeList](https://myanimelist.net) |
| `tmdb` | Yes | Fetches media metadata from [The Movie Database](https://www.themoviedb.org/settings/api) |

## Uploaders

| Uploader | Token required | Description |
|---|---|---|
| `imgur` | Yes | Hosts posters on [Imgur](https://imgur.com) |
| `imgbb` | Yes | Hosts posters temporarily on [ImgBB](https://imgbb.com) |
| `litterbox` | No | Hosts posters temporarily on [Litterbox](https://litterbox.catbox.moe) |
| `onlyimage` | Yes | Hosts posters temporarily on [OnlyImage](https://imgbb.com) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md).
