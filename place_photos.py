# -*- coding: utf-8 -*-
r"""index.html に img/ のイメージ写真6枚を配置する（2026-09-27）。

写真は ChatGPT 生成のイメージ（実写ではない）。各図版に「イメージ」のキャプションを付け、
顧客の製品・図面が写っているように見せない。配置は各節の導入文（H2直後の最初の段落）の直後。
既に <img が入っていれば何もしない。

    python place_photos.py
"""
import io
import os
import re

PLAN = [   # (ファイル名, 挿入先 section の目印, alt, キャプション)
    ("hero-lathe.jpg", '<section class="hero">', "旋盤で金属部品を加工しているところ（イメージ）", "旋盤加工のイメージ"),
    ("parts-table.jpg", 'id="service"', "加工を終えた金属部品が作業台に並ぶ様子（イメージ）", "加工品のイメージ"),
    ("packing.jpg", 'id="spec"', "木枠パレットに固定した梱包（イメージ）", "梱包・出荷のイメージ"),
    ("inspection.jpg", 'id="quality"', "ノギスで寸法を測る手元（イメージ）", "受入・出荷検査のイメージ"),
    ("drawing-meeting.jpg", 'id="flow"', "図面を見ながら打合せする手元（イメージ）", "図面の読み合わせのイメージ"),
    ("workshop.jpg", 'id="rep"', "整頓された町工場の作業場（イメージ）", "作業場のイメージ"),
]
CSS = """
  .photo{margin:22px 0 6px;border-radius:14px;overflow:hidden;background:#e9edf2}
  .photo img{width:100%;height:auto;display:block;aspect-ratio:16/9;object-fit:cover}
  .photo figcaption{font-size:12px;color:#5b6773;padding:6px 4px 0;text-align:right}
  .hero .photo{margin:26px 0 0;box-shadow:0 10px 30px rgba(0,0,0,.25)}
  .hero .photo figcaption{color:rgba(255,255,255,.75)}
"""


def main():
    d = io.open("index.html", encoding="utf-8").read()
    if "<img" in d:
        print("配置済み"); return
    missing = [f for f, *_ in PLAN if not os.path.exists(os.path.join("img", f))]
    if missing:
        print("画像が無い:", missing); return
    d = d.replace("</style>", CSS + "</style>", 1)
    for f, anchor, alt, cap in PLAN:
        i = d.find(anchor)
        assert i > 0, anchor
        # その section 内で H2（heroは H1）の後、最初の </p> の直後に入れる
        h = d.find("</h1>" if "hero" in anchor else "</h2>", i)
        p = d.find("</p>", h) + len("</p>")
        fig = ('\n    <figure class="photo"><img src="img/%s" alt="%s" loading="%s" width="1600" height="900">'
               '<figcaption>%s（写真はイメージです）</figcaption></figure>' % (f, alt, "eager" if "hero" in anchor else "lazy", cap))
        d = d[:p] + fig + d[p:]
        print("配置", f, "→", anchor)
    io.open("index.html", "w", encoding="utf-8").write(d)
    print("img:", d.count("<img"))


if __name__ == "__main__":
    main()
