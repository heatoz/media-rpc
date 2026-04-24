<div align="center">

# media-rpc

Event-based Discord Rich Presence integration for Media Players.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)](https://python.org)
[![Discord](https://img.shields.io/badge/Discord-Rich%20Presence-5865F2?logo=discord&logoColor=white)](https://discord.com)

<img src="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/s_movie.png" width="32%" />
<img src="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/s_movie2.png" width="32%" />
<img src="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/s_series.png" width="32%" />

</div>

## Usage

```
media-rpc
```

## Default Configuration

```toml
[player]
name = "mpc"
# port = 13579  # optional, defaults to 13579

# name = "jellyfin"
# host = "localhost"
# token = "your_token_here"
# user_name = "your_username"
# port = 8096  # optional, defaults to 8096
# ...

[adapter]
name = "imdb"
# name = "tmdb"
# token = "your_token_here"
# name = "mal"
# ...

[uploader]
name = "litterbox"
# name = "imgbb"
# token = "your_token_here"
# ...
```

## Players

| Player | Token required | Description |
|---|---|---|
| `mpc` | No | [MPC-HC](https://github.com/clsid2/mpc-hc) |
| `jellyfin` | Yes | [Jellyfin](https://jellyfin.org) Media Server |
| `plex` | Yes | [Plex](https://plex.tv) Media Server |

<details>
<summary><code>mpc</code> configuration</summary>

```toml
[player]
name = "mpc"
port = 13579  # optional, defaults to 13579
```

The MPC-HC web interface must be enabled under **View → Options → Web Interface**.

</details>

<details>
<summary><code>jellyfin</code> configuration</summary>

```toml
[player]
name = "jellyfin"
host = "localhost"
token = "your_token_here"
user_name = "your_username"
port = 8096  # optional, defaults to 8096
```

The API token can be generated in **Dashboard → API Keys**.

</details>

<details>
<summary><code>plex</code> configuration</summary>

```toml
[player]
name = "plex"
host = "localhost"
token = "your_token_here"
user_name = "your_username"
port = 32400  # optional, defaults to 32400
```

The API token can be obtained by clicking any item → **Get Info → View XML**
and copying the **X-Plex-Token** value from the URL.

</details>

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
