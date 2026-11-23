"""Contact sheet of a folder of run scripts: for each one, the view through its own camera, with its name under it.

Usage: python synth/sheet.py <dir> <out.png> [--cols 3] [--all-views] [--ids a,b,c]
The pictures are the three-view ones from run_sandboxed.py --own-view; without --all-views only the left third is shown.
Pictures made with --only-own-view are one view wide: pass --all-views for those. The request under each picture comes
from <dir>/requests.json if there is one, else from synth/requests*.json.
"""
import argparse, glob, json, os, textwrap
import matplotlib
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("dir"); ap.add_argument("out"); ap.add_argument("--cols", type=int, default=3)
ap.add_argument("--all-views", action="store_true"); ap.add_argument("--ids", default="")
a = ap.parse_args()
font = ImageFont.truetype(os.path.join(matplotlib.get_data_path(), "fonts/ttf/DejaVuSans.ttf"), 13)
names = [os.path.basename(f)[:-4] for f in sorted(glob.glob(os.path.join(a.dir, "*.png")))]
names = [n for n in names if not a.ids or n in a.ids.split(",")]
requests = {}
for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests*.json")) + glob.glob(os.path.join(a.dir, "requests.json")):
    requests.update({it["id"]: it["request"] for it in json.load(open(f))})
tiles = []
for n in names:
    im = Image.open(os.path.join(a.dir, n + ".png")).convert("RGB")
    tiles.append((n, im if a.all_views else im.crop((0, 0, im.width // 3, im.height))))
w, h, pad, strip = tiles[0][1].width, tiles[0][1].height, 8, 54
cols = min(a.cols, len(tiles)); rows = -(-len(tiles) // cols)
sheet = Image.new("RGB", (pad + cols * (w + pad), pad + rows * (h + strip + pad)), (250, 250, 248))
d = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(tiles):
    x, y = pad + (i % cols) * (w + pad), pad + (i // cols) * (h + strip + pad)
    sheet.paste(im, (x, y))
    d.text((x, y + h + 3), n, font=font, fill=(25, 28, 33))
    for k, line in enumerate(textwrap.wrap(requests.get(n, ""), int(w / 7.2))[:2]):      # the request, on two lines at most
        d.text((x, y + h + 19 + 16 * k), line, font=font, fill=(95, 102, 112))
sheet.save(a.out)
print("wrote", a.out, sheet.size)
