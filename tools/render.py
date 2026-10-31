"""Render text-on-screen Reels (1080x1920, 30fps) from one-beat-per-line scripts."""
import subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG, FG, ACCENT, MUTED = (11, 22, 40), (255, 255, 255), (242, 184, 48), (140, 155, 180)
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 = 90, 850, 230, 1440  # keeps clear of IG caption + action rail


def beat_seconds(line):
    # reading time, not speaking time: ~2.6 words/s plus a beat to land
    return max(1.8, len(line.split()) / 2.6 + 0.6)


def card(line, is_hook, progress):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    size = 92 if is_hook else 80
    font = ImageFont.truetype(BOLD, size)
    wrapped = textwrap.wrap(line, width=16 if is_hook else 18)
    lh = int(size * 1.25)
    y = (SAFE_Y0 + SAFE_Y1) // 2 - lh * len(wrapped) // 2
    for row in wrapped:
        d.text((SAFE_X0, y), row, font=font, fill=ACCENT if is_hook else FG)
        y += lh
    d.text((SAFE_X0, SAFE_Y0 + 20), "CASH COMPASS", font=ImageFont.truetype(BOLD, 34), fill=MUTED)
    d.rectangle([SAFE_X0, SAFE_Y1 - 12, SAFE_X0 + int((SAFE_X1 - SAFE_X0) * progress), SAFE_Y1], fill=ACCENT)
    return img


def render(script_path, out_path):
    lines = [l.strip() for l in open(script_path) if l.strip()]
    durs = [beat_seconds(l) for l in lines]
    total = sum(durs)
    assert 7 <= total <= 45, f"{out_path}: {total:.1f}s outside 7-45s"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    t = 0.0
    for i, (line, dur) in enumerate(zip(lines, durs)):
        base = card(line, i == 0, (t + dur) / total)
        n = round(dur * FPS)
        for f in range(n):
            # 6-frame fade in from background, except the hook which must be up at frame 1
            a = 1.0 if i == 0 else min(1.0, (f + 1) / 6)
            frame = base if a == 1.0 else Image.blend(Image.new("RGB", (W, H), BG), base, a)
            ff.stdin.write(frame.tobytes())
        t += dur
    ff.stdin.close()
    assert ff.wait() == 0, "ffmpeg failed"
    print(f"{out_path}: {len(lines)} cards, {total:.1f}s")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
