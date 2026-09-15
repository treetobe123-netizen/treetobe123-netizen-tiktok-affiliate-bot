"""HiggsField(LLM)を使わず、テンプレート文でTikTokキャプションを組み立てるモジュール

「マタイガジェット部」向け: 機能性・便利さを前面に出した実用トーン。
景品表示法対応のため、楽天の商品説明(catchcopy)を誇大な宣伝文句ごと引用せず、
keyword(検索ジャンル)とpriceだけを使う。
"""
import datetime

CAPTION_TEMPLATES = [
    "{kw}、地味に便利なやつ見つけた\n{price}円くらいから\n気になった方はプロフィールのリンクから",
    "また買いたくなるやつ、{kw}編\nこれは普通に使えそう\n詳しくはプロフィールのリンクから",
    "{kw}まわり、これ1個あると楽になるかも\n気になった方はプロフィールのリンクから",
    "地味だけど{kw}、選ぶの地味に大事\nこれは候補に入れてた\nプロフィールのリンクから見てみて",
    "{kw}、こういうのでいいんだよってやつ\n気になった方はプロフィールのリンクから",
    "最近見つけた{kw}系ガジェット\n{price}円前後で意外とちゃんとしてる\nプロフィールのリンクから",
    "{kw}で時短できるの地味にでかい\nこれ良さそうだった\n気になった方はプロフィールのリンクから",
]


def _pick(templates, seed_key):
    day_index = datetime.date.today().toordinal()
    idx = (day_index + sum(ord(c) for c in seed_key)) % len(templates)
    return templates[idx]


def build_template_caption(item):
    """item: pick_product.pyが出力するitem dict({"keyword":..., "price":...} を含む)"""
    kw = item.get("keyword", "").strip() or "気になるガジェット"
    price = item.get("price", "")
    template = _pick(CAPTION_TEMPLATES, kw)
    return template.format(kw=kw, price=price)
