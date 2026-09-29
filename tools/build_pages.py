# -*- coding: utf-8 -*-
"""加工事業部サイトのビルド。

- index.html の <style> を assets/style.css へ切り出し（初回のみ）
- 全ページ共通のヘッダー・フッター・スマホ固定バーを差し替え
- サービス別ページ（SUBPAGES）と 404.html、sitemap.xml を生成

使い方: python tools/build_pages.py
本文は掲載済みの事実（index.html）だけで書く。推測で数値・実績を足さない。
"""
import io, os, re, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://n-start-jp.github.io"
TODAY = datetime.date.today().isoformat()
TEL = "0721-68-7577"
MAIL = "sales@n-start.jp"


def rd(p):
    return io.open(os.path.join(ROOT, p), encoding="utf-8").read()


def wr(p, s):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    io.open(full, "w", encoding="utf-8", newline="\n").write(s)


# ---------------------------------------------------------------- 共通部品
NAV = [("/#service", "事業内容"), ("/#spec", "対応範囲"), ("/#quality", "品質管理"),
       ("/#flow", "ご依頼の流れ"), ("/#company", "会社概要")]

SUBPAGES_NAV = [("/senban/", "旋盤加工"), ("/flange/", "フランジ・ふた物の加工"),
                ("/stainless/", "ステンレス・難削材の加工"), ("/zumen-nashi/", "図面がない部品の製作"),
                ("/tehai/", "加工外注の手配・一括発注")]

HEADER = f"""<header>
  <div class="wrap hd">
    <a class="logo" href="/"><i>N</i><span><b>株式会社N.Start 加工事業部</b><small>金属加工・製造まわりの相談窓口｜大阪・富田林</small></span></a>
    <nav class="gnav" id="gnav" aria-label="メインメニュー">
      {"".join(f'<a href="{h}">{t}</a>' for h, t in NAV)}
      <div class="gnav-sp">
        <p>サービス別のご案内</p>
        {"".join(f'<a href="{h}">{t}</a>' for h, t in SUBPAGES_NAV)}
        <a class="sp-tel" href="tel:0721687577">{TEL}<small>平日受付・法人窓口</small></a>
        <a class="sp-btn" href="/#contact">無料でお見積り・ご相談</a>
      </div>
    </nav>
    <div class="hd-r">
      <a class="hd-tel" href="tel:0721687577"><b>{TEL}</b><small>平日受付・法人窓口</small></a>
      <a class="hd-btn" href="/#contact">お見積り・ご相談</a>
      <button class="menu-btn" type="button" aria-label="メニューを開く" aria-controls="gnav" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>"""

FOOTER = f"""<footer>
  <div class="wrap">
    <div class="ft">
      <div>
        <a class="logo" href="/"><i>N</i><span><b>株式会社N.Start 加工事業部</b><small>金属加工・製造まわりの相談窓口</small></span></a>
        <p>〒584-0014 大阪府富田林市川面町2丁目6-12<br>TEL <a href="tel:0721687577">{TEL}</a>（平日）　MAIL <a href="mailto:{MAIL}">{MAIL}</a></p>
      </div>
      <div class="fcols">
        <nav class="fnav">
          <a href="/#service">事業内容</a><a href="/#spec">対応範囲</a><a href="/#examples">対応例</a><a href="/#quality">品質管理</a><a href="/#flow">ご依頼の流れ</a><a href="/#faq">よくあるご質問</a><a href="/#company">会社概要</a><a href="/#contact">お問い合わせ</a>
        </nav>
        <nav class="fnav fnav-svc">
          {"".join(f'<a href="{h}">{t}</a>' for h, t in SUBPAGES_NAV)}
        </nav>
      </div>
    </div>
    <div class="copy"><span>適格請求書発行事業者 T5120101067599　／　掲載写真はイメージです（お客様の製品・図面ではありません）</span><span>© N.Start Inc.</span></div>
  </div>
</footer>

<div class="mbar">
  <a class="t" href="tel:0721687577">電話で相談</a>
  <a class="m" href="/#contact">無料でお見積り</a>
</div>

<script src="/assets/main.js" defer></script>"""

HEAD_LINKS = """<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">"""

EXTRA_CSS = r"""
/* ===== 共通追加（build_pages.py） ===== */
.menu-btn{display:none;width:52px;height:52px;border:0;background:transparent;cursor:pointer;flex-direction:column;justify-content:center;align-items:center;gap:6px;margin-right:12px}
.menu-btn span{display:block;width:26px;height:2px;background:var(--ink);transition:.2s}
body.nav-open .menu-btn span:nth-child(1){transform:translateY(8px) rotate(45deg)}
body.nav-open .menu-btn span:nth-child(2){opacity:0}
body.nav-open .menu-btn span:nth-child(3){transform:translateY(-8px) rotate(-45deg)}
.gnav-sp{display:none}
.fcols{display:flex;gap:56px;flex-wrap:wrap}
.fnav-svc{grid-template-columns:repeat(1,auto)}
.svc-links{margin-top:56px}
.svc-links h3{font-size:17px;font-weight:900;margin-bottom:18px}
.links{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.links a{display:flex;flex-direction:column;justify-content:space-between;gap:18px;min-height:128px;padding:22px 20px 18px;background:var(--main);color:#fff;font-weight:900;font-size:15px;line-height:1.5;transition:background .2s}
.links a:hover{background:var(--main-d)}
.links a small{display:block;font-family:var(--en);font-weight:600;font-size:12px;letter-spacing:.14em;color:var(--hero-en);margin-bottom:6px}
.links a:after{content:"";align-self:flex-end;width:9px;height:9px;border-top:2px solid #fff;border-right:2px solid #fff;transform:rotate(45deg)}

/* 下層ページ */
.phero{position:relative;height:400px;margin-top:76px;display:flex;align-items:flex-end;color:#fff;background:var(--main-d);overflow:hidden}
.phero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.phero:before{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(var(--rgb),.92) 0%,rgba(var(--rgb),.7) 50%,rgba(var(--rgb),.25) 100%)}
.phero .wrap{position:relative;z-index:2;width:100%;padding-bottom:56px}
.phero .en{font-family:var(--en);font-size:14px;font-weight:600;letter-spacing:.22em;color:var(--hero-en);margin-bottom:12px}
.phero h1{font-size:clamp(28px,3.6vw,44px);font-weight:900;line-height:1.4;letter-spacing:.03em;margin-bottom:14px}
.phero p.sub{max-width:640px;color:rgba(255,255,255,.9);font-size:16px}
.crumb{border-bottom:1px solid var(--line);font-size:12px;color:var(--sub)}
.crumb ol{display:flex;flex-wrap:wrap;gap:6px;padding:14px 0}
.crumb li:not(:last-child):after{content:"›";margin-left:6px;color:var(--line)}
.crumb a{color:var(--key);font-weight:700}
.sub-sec{padding:96px 0}
.cmp{width:100%;border-collapse:collapse;background:#fff}
.cmp th,.cmp td{padding:18px 22px;border:1px solid var(--line);font-size:15px;text-align:left;vertical-align:top}
.cmp thead th{background:var(--gray);font-size:14px}
.cmp thead th:last-child{background:var(--main);color:#fff}
.cmp tbody th{width:160px;background:var(--gray)}
.cmp td:last-child{font-weight:700;color:var(--key)}
.needs-box{background:var(--soft);padding:44px 48px}
.needs-box h3{font-size:20px;font-weight:900;margin-bottom:6px}
.needs-box .note{margin-bottom:24px}
.needs-box .needs-grid{grid-template-columns:repeat(4,1fr)}
.rel{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.nf{padding:200px 0 140px;text-align:center}
.nf .en{font-family:var(--en);font-size:120px;font-weight:700;line-height:1;color:var(--key)}
.nf h1{font-size:22px;font-weight:900;margin:18px 0 12px}
.nf p{color:var(--sub);margin-bottom:32px}

@media (max-width:1100px){
  .menu-btn{display:flex}
  .gnav{position:fixed;top:76px;left:0;right:0;bottom:0;background:#fff;flex-direction:column;gap:0;padding:12px 32px 40px;overflow-y:auto;display:none}
  body.nav-open .gnav{display:flex}
  body.nav-open{overflow:hidden}
  .gnav>a{padding:16px 0;border-bottom:1px solid var(--line);font-size:16px}
  .gnav a:after{display:none}
  .gnav-sp{display:flex;flex-direction:column}
  .gnav-sp p{font-size:12px;font-weight:700;color:var(--sub);margin:24px 0 4px}
  .gnav-sp a{padding:12px 0;border-bottom:1px solid var(--line);font-size:15px}
  .gnav-sp .sp-tel{border:0;margin-top:24px;font-family:var(--en);font-size:30px;font-weight:600;color:var(--key);line-height:1.1}
  .gnav-sp .sp-tel small{display:block;font-family:var(--jp);font-size:12px;color:var(--sub);font-weight:500;margin-top:4px}
  .gnav-sp .sp-btn{margin-top:18px;border:0;background:var(--btn);color:var(--btn-fg);text-align:center;padding:18px;font-weight:700}
  .links{grid-template-columns:repeat(3,1fr)}
  .rel{grid-template-columns:1fr 1fr}
  .needs-box .needs-grid{grid-template-columns:1fr 1fr}
}
@media (max-width:760px){
  .menu-btn{margin-right:-8px}
  .gnav{top:62px;padding:8px 16px 32px}
  .phero{margin-top:62px;height:340px}
  .phero .wrap{padding-bottom:36px}
  .phero p.sub{font-size:14px}
  .sub-sec{padding:64px 0}
  .links{grid-template-columns:1fr 1fr;gap:8px}
  .links a{min-height:110px;padding:18px 14px 14px;font-size:14px}
  .cmp,.cmp thead,.cmp tbody,.cmp tr,.cmp th,.cmp td{font-size:13px}
  .cmp th,.cmp td{padding:12px 10px}
  .cmp tbody th{width:84px}
  .needs-box{padding:28px 20px}
  .needs-box .needs-grid{grid-template-columns:1fr}
  .rel{grid-template-columns:1fr}
  .fcols{gap:28px}
  .nf{padding:140px 0 100px}
  .nf .en{font-size:84px}
}
"""

MAIN_JS = """(function(){
  var b=document.querySelector('.menu-btn');if(!b)return;
  function set(o){document.body.classList.toggle('nav-open',o);b.setAttribute('aria-expanded',o?'true':'false');b.setAttribute('aria-label',o?'メニューを閉じる':'メニューを開く');}
  b.addEventListener('click',function(){set(!document.body.classList.contains('nav-open'));});
  document.querySelectorAll('#gnav a').forEach(function(a){a.addEventListener('click',function(){set(false);});});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false);});
})();
"""

ORG = {"@type": "LocalBusiness", "@id": BASE + "/#org", "name": "株式会社N.Start 加工事業部",
       "url": BASE + "/", "telephone": "+81-721-68-7577", "email": MAIL,
       "logo": BASE + "/assets/icon-512.png", "image": BASE + "/img/hero-lathe.jpg",
       "address": {"@type": "PostalAddress", "streetAddress": "川面町2丁目6-12", "addressLocality": "富田林市",
                   "addressRegion": "大阪府", "postalCode": "584-0014", "addressCountry": "JP"},
       "areaServed": ["大阪府", "奈良県"]}


def picture(name, alt, sizes="100vw", eager=False):
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="/img/{name}.webp" srcset="/img/{name}-800.webp 800w, /img/{name}.webp 1600w" '
            f'sizes="{sizes}" alt="{alt}" width="1600" height="900" {load}>')


def cta_band():
    return f"""<div class="cta">
  <div class="wrap">
    <div>
      <h2>「頼めるかどうか」の確認だけでも、<br>お気軽にどうぞ。</h2>
      <p>お見積りは無料です。図面がなくても、材質が分からなくても、内容の整理から一緒に進めます。</p>
    </div>
    <div class="cta-box">
      <a class="cta-tel" href="tel:0721687577"><small>お電話<br>平日・法人窓口</small><b>{TEL}</b></a>
      <a class="btn btn-key" href="mailto:{MAIL}?subject=%E8%A6%8B%E7%A9%8D%E3%82%8A%E3%83%BB%E7%9B%B8%E8%AB%87%E3%81%AE%E4%BE%9D%E9%A0%BC">メールでお見積り・ご相談</a>
    </div>
  </div>
</div>"""


NEEDS = """<div class="needs-box">
  <h3>お見積りのときに教えていただきたいこと</h3>
  <p class="note">4つとも揃っていなくて大丈夫です。分かる範囲でお知らせください。</p>
  <div class="needs-grid">
    <div><b>何を</b><span>図面・写真・現物・手描きスケッチのいずれか</span></div>
    <div><b>いくつ</b><span>1個でも、継続で毎月でも</span></div>
    <div><b>いつまでに</b><span>希望納期。急ぎならその旨を最初に</span></div>
    <div><b>どこまで</b><span>加工のみ／塗装・組立まで／検査成績書の要否</span></div>
  </div>
</div>"""

MATS = '<div class="mats"><span>炭素鋼（S45C・SS400 など）</span><span>ステンレス（SUS303・304・316 など）</span><span>鋳鋼・鋳鉄</span><span>アルミ</span><span>銅・真鍮</span><span>チタン・特殊合金（難削材）</span><span>樹脂</span></div>'
INSPECT = '受入・完了・出荷の3段階で当社が検査します。協力工場の検査をもって当社の検査に代えることはしません。<span class="note">検査成績書（寸法測定結果と判定）はご要望に応じて発行します。記録は3年間保管します。</span>'
DRAWING = '紙図面、PDF、手描きスケッチ、現物、写真のいずれでも。<span class="note">図面がない場合は、現物や用途をお聞きして、必要な情報を当社で整理します。</span>'
LOT = '<b>1個から。</b>単品・試作から繰り返しの量産まで。<span class="note">量産は初品の寸法確認（初品検査）を行ってから本数に入る進め方を基本にしています。</span>'

# ---------------------------------------------------------------- サービス別ページ
SUBPAGES = [
 dict(slug="senban", img="hero-lathe", img_alt="旋盤で金属部品を加工しているところ（イメージ）",
  title="旋盤加工の相談窓口｜丸物・軸物・フランジを1個から｜大阪 N.Start加工事業部",
  desc="旋盤加工（外径・内径・段付き・溝・ねじ）を1個の試作から量産まで。主力はステンレス・難削材。穴あけ・熱処理・塗装・組立などの後工程までまとめて手配し、受入・完了・出荷の3段階で当社が検査します。大阪府富田林市。",
  en="TURNING", h1="旋盤加工", crumb="旋盤加工",
  sub="丸物・軸物・フランジを、1個の試作から量産まで。後工程の穴あけ・塗装・組立まで、まとめてお引き受けします。",
  ov_h2="旋盤加工で対応すること",
  ov_lead="外径・内径・段付き・溝・ねじといった旋盤加工を、形状と材質に合った協力工場へ手配し、当社が検査してから納品します。「旋盤だけ頼みたい」も「旋盤のあとに穴あけと塗装まで」も、窓口は当社ひとつです。",
  cards=[("丸物・軸物", "旋盤による外径・内径・段付き・溝加工。"),
         ("フランジ・ふた物", "座面仕上げのあと、ボルト穴の多数あけやザグリまで一続きで。"),
         ("長尺物", "たわみ・振れを抑える段取りで加工し、2点以上で結束して梱包します。"),
         ("ねじ・タップ加工", "ねじ部はねじゲージで通り・止まりを確認してから出荷します。"),
         ("支給材への加工", "鋳造品・鍛造品・半製品を支給いただき、仕上げ加工を行います。"),
         ("追加工・改造", "市販品や既存部品への穴追加・ねじ追加も承ります。")],
  spec=[("加工内容", "OPERATION", "外径・内径・段付き・溝・ねじ加工、面取り・バリ取り。"),
        ("設備", "EQUIPMENT", "NC旋盤・汎用機などを持つ協力工場のネットワークから、形状・数量に合わせて手配します。"),
        ("材質", "MATERIAL", MATS + '<span class="note">主力はステンレスと特殊材（難削材）。材質が分からない場合は、現物や用途からご一緒に選定します。</span>'),
        ("ロット", "LOT", LOT),
        ("後工程", "NEXT PROCESS", "穴あけ・ザグリ・タップ（フライス・マシニング）、研削、熱処理・表面処理・めっき、塗装、組立まで一括で手配します。"),
        ("検査", "INSPECTION", INSPECT),
        ("図面・データ", "DRAWING", DRAWING)],
  faq=[("1個だけの旋盤加工でも頼めますか？", "はい、1個から承ります。試作品、壊れた部品の代替、設備の補修部品など、単品のご依頼こそ歓迎です。"),
       ("旋盤加工のあとの穴あけや塗装も、まとめて頼めますか？", "はい。穴あけ・ザグリ・タップ、熱処理・表面処理、塗装、組立まで一括で手配し、完成品としてお納めします。"),
       ("材質が分からない部品でも大丈夫ですか？", "大丈夫です。用途や現物をお聞きして、ご一緒に選定します。"),
       ("図面がなく、現物しかありません。", "現物・写真・手描きスケッチから、必要な寸法や仕様を当社で整理してお見積りします。詳しくは「図面がない部品の製作」のページをご覧ください。")]),

 dict(slug="flange", img="parts-table", img_alt="加工を終えたフランジが作業台に並ぶ様子（イメージ）",
  title="フランジ加工の相談窓口｜座面仕上げ・多数穴あけ・ザグリ｜大阪 N.Start加工事業部",
  desc="フランジ・ふた物の旋盤加工、座面仕上げ、ボルト穴の多数あけ、ザグリを1枚から。鋳造品・鍛造品など支給材への追加工も承ります。シール面の打痕・傷、穴の位置と数量を当社が検査して納品します。大阪府富田林市。",
  en="FLANGE", h1="フランジ・ふた物の加工", crumb="フランジ・ふた物の加工",
  sub="座面仕上げ、ボルト穴の多数あけ、ザグリまで。1枚から量産まで、検査してお納めします。",
  ov_h2="フランジ加工で対応すること",
  ov_lead="フランジやふた物は、旋盤で外径・内径・座面を仕上げたあと、ボルト穴をあけ、必要に応じてザグリやタップを加える、工程が複数にまたがる品物です。当社は工程ごとの協力工場への手配から、検査・梱包・出荷までをまとめ、お客様の窓口をひとつにします。",
  cards=[("座面・シール面の仕上げ", "旋盤による外径・内径・座面の仕上げ。機能面・シール面の打痕・傷は、外観検査の重点項目です。"),
         ("ボルト穴の多数あけ", "穴の位置・数量を図面と照合し、加工忘れを防ぎます。"),
         ("ザグリ・タップ", "穴あけ後のザグリ、タップ・ねじ加工。ねじ部はねじゲージで確認します。"),
         ("支給材への追加工", "鋳造品・鍛造品・半製品を支給いただき、仕上げ加工を行います。受入時に品名・数量・外観を確認・記録します。"),
         ("重量物の梱包・出荷", "形状・重量に応じて梱包します。20kgを超える重量物も、取り扱いの区分を定めて扱っています。"),
         ("量産は初品確認から", "初品の寸法確認（初品検査）を行ってから、本数の加工に入ります。")],
  spec=[("加工内容", "OPERATION", "外径・内径・座面の旋盤加工、ボルト穴あけ、ザグリ、タップ・ねじ加工、面取り・バリ取り。"),
        ("材質", "MATERIAL", MATS + '<span class="note">主力はステンレスと特殊材（難削材）です。</span>'),
        ("ロット", "LOT", LOT.replace("1個から", "1枚から")),
        ("サイズ", "SIZE", '手のひらに載る小物から、フォークリフトで扱う重量物まで。<span class="note">加工できる最大寸法は形状・工程によって変わるため、お見積り時に個別にお答えします。</span>'),
        ("支給材", "SUPPLIED", "お客様支給の鋳造品・鍛造品・半製品への加工、追加工を承ります。"),
        ("検査", "INSPECTION", INSPECT),
        ("主な分野", "FIELD", "産業機械・配管機器・設備の部品。分野は問いません。")],
  faq=[("1枚だけでも頼めますか？", "はい、1枚から承ります。補修用の1枚や試作もご相談ください。"),
       ("鋳造品を支給して、加工だけ頼めますか？", "承ります。受入時に品名・数量・外観を確認して記録し、加工後は完了・出荷の検査を経て納品します。支給品に関わる不具合が見つかった場合は速やかにご報告します。"),
       ("検査成績書は出せますか？", "ご要望に応じて、寸法測定結果と判定をまとめた検査成績書を納品時に添付します。量産品は初品の寸法測定記録から始めます。"),
       ("数量が多い場合の進め方は？", "初品の寸法確認（初品検査）を行ってから本数に入る進め方を基本にしています。数量・納期に合わせて、工程の組み方をご提案します。")]),

 dict(slug="stainless", img="workshop", img_alt="金属加工の作業場（イメージ）",
  title="ステンレス・難削材の加工｜SUS303・304・316、チタン・特殊合金｜大阪 N.Start加工事業部",
  desc="ステンレス（SUS303・304・316など）やチタン・特殊合金などの難削材の加工を1個から。主力はステンレスと特殊材。材質に合った協力工場を選んで手配し、さび・変色の確認を含む外観検査のうえ納品します。ミルシートの手配も可能。大阪府富田林市。",
  en="STAINLESS / HARD-TO-CUT", h1="ステンレス・難削材の加工", crumb="ステンレス・難削材の加工",
  sub="当社の主力はステンレスと特殊材。材質に合った協力工場を選び、検査してからお納めします。",
  ov_h2="ステンレス・難削材の加工",
  ov_lead="ステンレスやチタン、特殊合金は、刃物の摩耗や加工中の熱の影響を受けやすく、同じ図面でも頼む先によって仕上がり・納期・価格に差が出やすい材料です。当社は材質と形状を見たうえで協力工場を選んで手配し、受入・完了・出荷の3段階で検査してからお納めします。",
  cards=[("ステンレス", "SUS303・304・316 など。当社の主力材料です。"),
         ("チタン・特殊合金", "難削材と呼ばれる材料も、まずご相談ください。"),
         ("炭素鋼", "S45C・SS400 など。"),
         ("鋳鋼・鋳鉄", "支給の鋳造品への仕上げ加工も承ります。"),
         ("アルミ・銅・真鍮", "非鉄金属の加工も手配します。"),
         ("樹脂", "金属以外の材料もご相談ください。")],
  spec=[("加工内容", "OPERATION", "旋盤、フライス・マシニング、穴あけ・ザグリ・タップ、研削、溶接・製缶、熱処理・表面処理・めっき。"),
        ("材質の選定", "SELECTION", "材質が分からない場合は、現物や用途（使う環境・求める性質）をお聞きして、ご一緒に選定します。"),
        ("ミルシート", "MILL SHEET", "材料証明（ミルシート）は、材料手配の段階で必要とお伝えいただければ、取得できるよう手配します。"),
        ("外観検査", "APPEARANCE", "打痕・傷、バリ、切りくず・異物、加工面の状態（びびり・むしれ）、さび・変色と防錆処理など8項目を確認します。"),
        ("ロット", "LOT", LOT),
        ("検査", "INSPECTION", INSPECT)],
  faq=[("SUS304とSUS316、どちらがいいか分かりません。", "ご用途（使う環境・求める性質）をお聞きしたうえで、ご一緒に選定します。材質の呼び方が分からなくても大丈夫です。"),
       ("ミルシートは出せますか？", "材料手配の段階で必要とお伝えいただければ、取得できるよう手配します。"),
       ("難削材の単品でも頼めますか？", "はい、1個から承ります。精度・納期・価格のどれかが成り立たない場合は、引き受ける前に正直にお伝えし、代わりの方法をご提案します。"),
       ("ISOは取得していますか？", "ISO 9001 は取得していません。品質方針・社内標準・工程管理表・外観検査基準・梱包出荷標準・計測器校正規程を整備し、記録を3年間保管する運用をしています。")]),

 dict(slug="zumen-nashi", img="drawing-meeting", img_alt="図面を見ながら打合せする手元（イメージ）",
  title="図面がない部品の製作・再製作｜現物・写真から｜大阪 N.Start加工事業部",
  desc="図面がない部品も、現物・写真・手描きスケッチからご相談いただけます。必要な寸法や仕様を当社で整理してからお見積り。長年の加工先が廃業・縮小した部品の引き継ぎ、従来品の再製作、代替材のご相談も。大阪府富田林市。",
  en="NO DRAWING", h1="図面がない部品の製作・再製作", crumb="図面がない部品の製作",
  sub="現物・写真・手描きスケッチからでも大丈夫です。加工先の廃業で困っている部品の引き継ぎもご相談ください。",
  ov_h2="図面がなくても、ご相談いただけます",
  ov_lead="「図面がないから頼めない」と諦める必要はありません。現物や写真、用途をお聞きして、必要な寸法や仕様を当社で整理し、お見積りに進みます。図面の作成が必要な場合は、その旨と進め方を最初にご提案します。",
  cards=[("壊れた部品と同じものがほしい", "現物や破損品をもとに、必要な寸法や仕様を整理します。"),
         ("長年の加工先が廃業・縮小した", "図面と現物があれば引き継げます。従来品の再製作、追加工、代替材の相談まで対応します。"),
         ("手描きのスケッチしかない", "手描きスケッチや写真からでも、ご相談いただけます。"),
         ("材質が分からない", "現物や用途をお聞きして、ご一緒に選定します。"),
         ("専門用語が分からない", "「ここに穴を増やしたい」「この部品を同じものにしたい」といった言葉で十分です。"),
         ("1個だけ必要", "設備の補修部品など、単品のご依頼こそ歓迎です。")],
  spec=[("お手元にあるもの", "MATERIALS", "現物、写真、手描きスケッチ、古い図面など、お手元にあるものでご相談ください。"),
        ("内容の整理", "ARRANGE", "必要な寸法・仕様・材質を当社で整理します。分からない点、決めきれない点は、こちらから質問します。"),
        ("図面の作成", "DRAWING", "図面の作成が必要な場合は、その旨と進め方をお見積りの段階でご提案します。"),
        ("再製作・引き継ぎ", "REMAKE", "従来品の再製作、追加工、代替材のご相談まで対応します。"),
        ("ロット", "LOT", LOT),
        ("検査", "INSPECTION", INSPECT)],
  faq=[("写真だけでお見積りできますか？", "写真と用途をお聞きして、必要な情報を整理します。写真だけでは決めきれない点がある場合は、こちらから確認のご連絡をします。"),
       ("図面を作ってもらえますか？", "図面の作成が必要な場合は、その旨と進め方をご提案します。"),
       ("加工先が廃業してしまいました。同じものを作れますか？", "図面と現物があれば引き継げます。図面がない場合も、現物から必要な情報を整理してご相談に乗ります。"),
       ("相談だけでも構いませんか？", "構いません。ご相談だけで終わっても費用はいただきません。「頼めるかどうかの確認だけ」でもお気軽にどうぞ。")]),

 dict(slug="tehai", img="packing", img_alt="木枠パレットに固定した梱包（イメージ）",
  title="加工外注の手配代行・一括発注｜複数工程を窓口ひとつで｜大阪 N.Start加工事業部",
  desc="旋盤・穴あけ・熱処理・塗装・組立など、工程ごとに分かれる加工外注を当社が一括で手配。協力工場の選定・発注・納期管理・受入検査・梱包出荷、請求まで窓口はひとつ。製造部長・工場長として外注管理を担ってきた代表が対応します。大阪府富田林市。",
  en="ONE WINDOW", h1="加工外注の手配・一括発注", crumb="加工外注の手配・一括発注",
  sub="工程ごとの外注先探し・発注・納期管理・検査を、当社がまとめてお引き受けします。",
  ov_h2="窓口は、当社ひとつ",
  ov_lead="部品ひとつでも、旋盤→穴あけ→熱処理→塗装→組立と工程が分かれると、頼み先ごとの連絡、納期の追いかけ、届いた品物の確認に手間がかかります。産業機器メーカーで製造部長・工場長として外注先の選定・評価を担ってきた代表が、その部分ごとお引き受けします。",
  cards=[("協力工場の選定・発注", "工程ごとに、形状・材質・数量に合った協力工場を選んで発注します。"),
         ("材料・規格品の調達", "加工に必要な材料や規格品の調達も承ります。"),
         ("納期管理・進捗のご報告", "工程ごとの進み具合を当社が管理し、ご報告します。"),
         ("受入検査ののち、まとめて納品", "協力工場の検査をもって、当社の検査に代えることはしません。"),
         ("組立・塗装まで", "加工→表面処理・塗装→組立まで手配し、完成品としてお納めします。"),
         ("お支払い・請求も一本化", "請求は当社からまとめて。適格請求書（インボイス）に対応しています。")],
  cmp=[("連絡先", "工程ごとに複数の加工先", "当社ひとつ"),
       ("納期管理", "各社を個別に追いかける", "当社が管理し、進捗をご報告"),
       ("検査", "届いた品物をお客様が確認", "当社が受入・完了・出荷の3段階で検査"),
       ("請求", "各社から個別に届く", "当社からまとめて1通")],
  spec=[("手配できる工程", "PROCESS", "旋盤・フライス・マシニング、穴あけ・タップ、研削、ワイヤー放電、溶接・製缶・板金、曲げ、熱処理、めっき・表面処理、塗装、組立、洗浄、刻印・識別表示、検査・測定、梱包・出荷。"),
        ("検査", "INSPECTION", INSPECT),
        ("お支払い", "PAYMENT", "銀行振込。請求書発行日の翌月5日まで（振込手数料はお客様負担）。継続取引の条件はご相談ください。"),
        ("機密", "CONFIDENTIAL", "お預かりした図面・情報は、見積・製作の目的以外に使用しません。協力工場へ渡す情報も必要な範囲に限ります。秘密保持契約が必要な場合は、お取引前に締結します。")],
  faq=[("工程が多い部品でも、まとめて頼めますか？", "はい。加工→表面処理・塗装→組立まで一括で手配し、完成品としてお納めします。"),
       ("検査成績書は出せますか？", "ご要望に応じて、寸法測定結果と判定をまとめた検査成績書を発行します。"),
       ("図面は協力工場にそのまま渡されますか？", "協力工場へ渡す情報は必要な範囲に限ります。秘密保持契約が必要な場合は、お取引前に締結します。"),
       ("対応地域は？", "大阪府・奈良県を中心とした近畿圏です。配送での納品も承ります。")]),
]


def head(title, desc, path, ld):
    return f"""<!DOCTYPE html>
<html lang="ja" data-theme="blue">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ja_JP">
<meta property="og:image" content="{BASE}/img/hero-lathe.jpg">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{HEAD_LINKS}
</head>
<body>

{HEADER}
"""


def subpage(p):
    path = f"/{p['slug']}/"
    ld = {"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "Service", "name": p["h1"], "description": p["desc"], "url": BASE + path,
         "provider": {"@id": BASE + "/#org"}, "areaServed": ["大阪府", "奈良県"]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ホーム", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": p["crumb"], "item": BASE + path}]}]}
    cards = "".join(f'<li><span class="n">POINT {i:02d}</span><h3>{t}</h3><p>{d}</p></li>'
                    for i, (t, d) in enumerate(p["cards"], 1))
    spec = "".join(f'<tr><th>{a}<small>{b}</small></th><td>{c}</td></tr>' for a, b, c in p["spec"])
    faq = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><div class="a"><p>{a}</p></div></details>'
                  for i, (q, a) in enumerate(p["faq"]))
    faq = faq.replace("「図面がない部品の製作」のページ", '<a href="/zumen-nashi/" style="color:var(--key);font-weight:700">「図面がない部品の製作」</a>のページ')
    rel = "".join(f'<a href="{h}"><span><small>SERVICE</small>{t}</span></a>' for h, t in SUBPAGES_NAV if h != path)
    cmp = ""
    if p.get("cmp"):
        rows = "".join(f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in p["cmp"])
        cmp = f"""<h3 class="q-h" style="margin-top:64px">個別に手配する場合との違い</h3>
    <table class="cmp"><thead><tr><th></th><th>工程ごとに個別に手配</th><th>当社に一括でご依頼</th></tr></thead><tbody>{rows}</tbody></table>"""
    body = f"""<main id="top">

<section class="phero">
  {picture(p['img'], p['img_alt'], eager=True)}
  <div class="wrap">
    <p class="en">{p['en']}</p>
    <h1>{p['h1']}</h1>
    <p class="sub">{p['sub']}</p>
  </div>
</section>
<nav class="crumb" aria-label="パンくずリスト"><div class="wrap"><ol><li><a href="/">ホーム</a></li><li>{p['crumb']}</li></ol></div></nav>

<section class="sub-sec">
  <div class="wrap">
    <div class="ttl-row">
      <div class="ttl"><span class="en">Overview</span><h2>{p['ov_h2']}</h2></div>
      <p class="lead">{p['ov_lead']}</p>
    </div>
    <ul class="cases">{cards}</ul>
    {cmp}
  </div>
</section>

<section class="sub-sec bg-gray">
  <div class="wrap">
    <div class="ttl"><span class="en">Detail</span><h2>対応内容</h2></div>
    <table class="spec">{spec}</table>
  </div>
</section>

<section class="sub-sec">
  <div class="wrap">
    {NEEDS}
  </div>
</section>

<section class="sub-sec" style="padding-top:0">
  <div class="wrap">
    <div class="ttl center"><span class="en">FAQ</span><h2>よくあるご質問</h2></div>
    <div class="faq">{faq}</div>
    <p class="note" style="text-align:center;margin-top:24px"><a href="/#faq" style="color:var(--key);font-weight:700">よくあるご質問をもっと見る</a></p>
  </div>
</section>

{cta_band()}

<section class="sub-sec bg-gray">
  <div class="wrap">
    <div class="ttl"><span class="en">Other Services</span><h2>そのほかのご案内</h2></div>
    <div class="links rel">{rel}</div>
  </div>
</section>

</main>

{FOOTER}

</body>
</html>
"""
    return head(p["title"], p["desc"], path, ld) + body


def page_404():
    ld = {"@context": "https://schema.org", **ORG}
    return head("ページが見つかりません｜N.Start加工事業部", "お探しのページは見つかりませんでした。", "/404.html", ld).replace(
        '<link rel="canonical" href="https://n-start-jp.github.io/404.html">', '<meta name="robots" content="noindex">') + f"""<main>
<section class="nf">
  <div class="wrap">
    <p class="en">404</p>
    <h1>お探しのページは見つかりませんでした</h1>
    <p>移動または削除された可能性があります。トップページからお探しください。</p>
    <a class="btn btn-main" href="/">トップページへ</a>
  </div>
</section>
</main>

{FOOTER}

</body>
</html>
"""


# ---------------------------------------------------------------- index.html の整備
def build_index():
    s = rd("index.html")
    m = re.search(r"<style>(.*?)</style>", s, re.S)
    if m:  # 初回：CSS を切り出す
        wr("assets/style.css", m.group(1).strip() + "\n" + EXTRA_CSS)
        s = s.replace(m.group(0), "")
    else:  # 2回目以降：共通追加分だけ差し替える
        css = rd("assets/style.css")
        css = css.split("\n/* ===== 共通追加（build_pages.py） ===== */")[0].rstrip() + "\n" + EXTRA_CSS
        wr("assets/style.css", css)
    # 旧フォント読み込み・favicon を消して共通の head リンクへ
    s = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", s)
    s = re.sub(r'<link href="https://fonts.googleapis.com[^>]*>\s*', "", s)
    s = re.sub(r'<link rel="(icon|apple-touch-icon|stylesheet)"[^>]*>\s*', "", s)
    s = s.replace("</head>", HEAD_LINKS + "\n</head>", 1)
    # タイトル・説明
    t = "金属加工の相談窓口｜1個から・図面なしOK｜大阪・富田林 N.Start加工事業部"
    s = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", s)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t}">', s)
    # 構造化データ
    ld = {"@context": "https://schema.org", **ORG,
          "description": "旋盤・フライス・穴あけ・ねじ加工から組立・塗装、外注先の手配、検査・梱包出荷まで。金属加工と製造まわりの困りごとを1個から相談できる窓口です。"}
    s = re.sub(r'<script type="application/ld\+json">.*?</script>',
               f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>', s, count=1, flags=re.S)
    # ヘッダー・フッター・固定バー・スクリプト
    s = re.sub(r"<header>.*?</header>", HEADER, s, count=1, flags=re.S)
    s = re.sub(r"<footer>.*?</body>", FOOTER + "\n\n</body>", s, count=1, flags=re.S)
    # 画像を WebP・srcset に
    sizes = {"hero-lathe": "100vw", "parts-table": "100vw", "workshop": "(max-width:1100px) 100vw, 50vw",
             "inspection": "(max-width:1100px) 100vw, 50vw", "drawing-meeting": "(max-width:1100px) 100vw, 420px"}

    def repl(mm):
        tag = mm.group(0)
        name = re.search(r'src="/?img/([\w-]+)\.(?:jpg|webp)"', tag).group(1)
        alt = re.search(r'alt="([^"]*)"', tag).group(1)
        return picture(name, alt, sizes.get(name, "100vw"), eager=(name == "hero-lathe"))
    s = re.sub(r'<img src="/?img/[\w-]+\.(?:jpg|webp)"[^>]*>', repl, s)
    # サービス別ページへの導線（事業内容の直後）
    links = ('<div class="svc-links"><h3>サービス別のご案内</h3><div class="links">'
             + "".join(f'<a href="{h}"><span><small>SERVICE</small>{t}</span></a>' for h, t in SUBPAGES_NAV)
             + "</div></div>")
    s = re.sub(r'\s*<div class="svc-links">.*?</div></div>', "", s, flags=re.S)
    s = s.replace('</div>\n  </div>\n</section>\n\n<div class="banner">', '</div>\n    ' + links + '\n  </div>\n</section>\n\n<div class="banner">', 1)
    # ページ内リンクは / 付きに統一（下層と共通化）
    s = s.replace('href="#top"', 'href="/"')
    wr("index.html", s)


def build_sitemap():
    urls = ["/"] + [f"/{p['slug']}/" for p in SUBPAGES]
    body = "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    wr("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n')


if __name__ == "__main__":
    build_index()
    wr("assets/main.js", MAIN_JS)
    for p in SUBPAGES:
        wr(f"{p['slug']}/index.html", subpage(p))
    wr("404.html", page_404())
    build_sitemap()
    print("built:", ["index.html"] + [p["slug"] for p in SUBPAGES] + ["404.html", "sitemap.xml"])
