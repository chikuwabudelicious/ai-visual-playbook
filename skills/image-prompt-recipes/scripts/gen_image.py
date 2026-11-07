# -*- coding: utf-8 -*-
"""Generate or edit one image with the OpenAI Images API (gpt-image family).

    python gen_image.py --prompt-file p.txt --size 1536x1024 -o out/fig.png [--trim]
    python gen_image.py --prompt "..." --transparent --size 1024x1024 -o out/icon.png
    python gen_image.py --edit out/fig.png --prompt-file relang.txt -o out/fig_th.png
    python gen_image.py --prompt-file p.txt --dry          # show prompt / model / cost estimate only

Requires: pip install openai pillow ; env OPENAI_API_KEY.
Model order: --model, else env IMAGE_MODEL, else MODELS below. Falls back to the next one on 403/404 only.
Model names change; check `client.models.list()` before trusting the list (names valid as of 2026-11).
"""
import argparse, base64, os, sys
from pathlib import Path

MODELS = ["gpt-image-2.6-sunburst", "gpt-image-2.5-sunburst", "gpt-image-2"]
PRICE = 0.30            # rough USD per high-quality image (2026-11), for --dry only


def trim(path, tol=12, pad=0.02):
    """Crop the uniform border (colour of the top-left pixel), keep a small padding. Writes <name>_t.png."""
    from PIL import Image, ImageChops
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > tol else 0)
    box = diff.getbbox()
    if not box:
        return path
    p = int(max(im.size) * pad)
    box = (max(0, box[0] - p), max(0, box[1] - p), min(im.width, box[2] + p), min(im.height, box[3] + p))
    out = Path(path).with_name(Path(path).stem + "_t.png")
    im.crop(box).save(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt"), ap.add_argument("--prompt-file")
    ap.add_argument("--edit", help="source image: edit it instead of generating (e.g. swap text language)")
    ap.add_argument("--size", default="1536x1024")
    ap.add_argument("--quality", default="high")
    ap.add_argument("--transparent", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--trim", action="store_true", help="also write a border-trimmed copy (<name>_t.png)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    prompt = Path(a.prompt_file).read_text(encoding="utf-8") if a.prompt_file else a.prompt
    if not prompt:
        sys.exit("--prompt or --prompt-file is required")
    models = [a.model] if a.model else ([os.environ["IMAGE_MODEL"]] if os.environ.get("IMAGE_MODEL") else []) + MODELS
    if a.dry:
        print("models:", " -> ".join(models), "| size:", a.size, "| ~$%.2f" % PRICE)
        print(prompt)
        return
    try:
        import truststore                      # use the OS certificate store (corporate TLS inspection)
        truststore.inject_into_ssl()
    except ImportError:
        pass
    from openai import OpenAI, NotFoundError, PermissionDeniedError
    client = OpenAI()
    kw = dict(prompt=prompt, size=a.size, quality=a.quality, n=1)
    if a.transparent:
        kw.update(background="transparent", output_format="png")
    last = None
    for m in models:
        try:
            if a.edit:
                with open(a.edit, "rb") as f:
                    r = client.images.edit(model=m, image=f, **{k: v for k, v in kw.items() if k != "background"})
            else:
                r = client.images.generate(model=m, **kw)
            break
        except (NotFoundError, PermissionDeniedError) as e:     # model missing / not allowed -> next one
            print("skip %s: %s" % (m, str(e)[:120]), file=sys.stderr)
            last = e
    else:
        sys.exit("no model worked: %s" % last)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(r.data[0].b64_json))
    print("OK", out, "(%s)" % m)
    if a.trim:
        print("trimmed", trim(out))


if __name__ == "__main__":
    main()
