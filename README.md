# cashcompass-media

Hosting for Cash Compass (@cashcompass.co) Instagram reels. Metricool fetches the MP4s from the raw URLs.

- `reels/<week-monday>/cash-compass-reel-N.mp4`: the rendered reels
- `scripts/<week-monday>/reel-N.txt`: one beat per line; first line is the hook
- `tools/render.py`: `python3 tools/render.py script.txt out.mp4` renders a 1080x1920 navy/gold text reel (needs Pillow + ffmpeg)
- `POSTED.md`: every topic already used. Check it before writing new reels.
