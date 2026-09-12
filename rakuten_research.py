"""楽天市場APIから商品候補を取得するモジュール"""
import urllib.request
import urllib.parse
import urllib.error
import json

SEARCH_ENDPOINT = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"

# 日替わりでローテーションするリサーチキーワード
# 「マタイガジェット部」の軸：ガジェット・便利家電・一人暮らし向け時短グッズ中心
# (TikTok Shop Japanで家電・ガジェットが取引額1位カテゴリのため。育児・美容系はこのアカウントでは対象外)
KEYWORDS = [
    "モバイルバッテリー 大容量",
    "ワイヤレスイヤホン 人気",
    "スマホスタンド 便利",
    "USB充電器 急速",
    "LEDライト 便利グッズ",
    "デスク周り 便利グッズ",
    "一人暮らし 時短家電",
    "掃除グッズ 便利",
    "スマートウォッチ 人気",
    "Bluetoothスピーカー",
    "スマホ 三脚 自撮り",
    "収納グッズ 便利",
    "卓上 小型家電",
    "加湿器 卓上",
    "USBファン 小型",
    "ケーブル 収納 便利",
    "モニター 折りたたみ",
]


def _get_json(url, headers=None, env=None):
    """envにRAKUTEN_PROXY_URLがあれば、固定IPの中継プロキシ経由で取得する
    （楽天APIのIP許可リストがGitHub Actionsの流動IPと相性が悪いための回避策）
    """
    proxy_url = (env or {}).get("RAKUTEN_PROXY_URL")
    if proxy_url:
        target = f"{proxy_url}?{urllib.parse.urlencode({'url': url})}"
        req = urllib.request.Request(
            target, headers={"X-Proxy-Secret": env["RAKUTEN_PROXY_SECRET"]}
        )
    else:
        req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode())


def search_items(env, keyword, hits=10, sort="-reviewCount"):
    """キーワードで商品検索し、候補リストを返す"""
    params = urllib.parse.urlencode({
        "applicationId": env["RAKUTEN_APPLICATION_ID"],
        "accessKey": env["RAKUTEN_ACCESS_KEY"],
        "affiliateId": env["RAKUTEN_AFFILIATE_ID"],
        "keyword": keyword,
        "hits": hits,
        "sort": sort,
        "format": "json",
    })
    data = _get_json(
        f"{SEARCH_ENDPOINT}?{params}",
        headers={"Referer": env.get("GITHUB_PAGES_URL", "https://example.com")},
        env=env,
    )
    items = []
    for entry in data.get("Items", []):
        it = entry["Item"]
        items.append({
            "name": it.get("itemName"),
            "price": it.get("itemPrice"),
            "url": it.get("affiliateUrl") or it.get("itemUrl"),
            "image": (it.get("mediumImageUrls") or [{}])[0].get("imageUrl", ""),
            "shop": it.get("shopName"),
            "review_avg": it.get("reviewAverage"),
            "review_count": it.get("reviewCount"),
            "keyword": keyword,
            # ショップが書いたキャッチコピー・商品説明。悩み訴求やFAQが含まれることが多く、
            # 投稿文で「本当の売りポイント」を探すのに使う。説明文は長いため先頭700文字に切る
            "catchcopy": it.get("catchcopy", ""),
            "caption": (it.get("itemCaption") or "")[:700],
        })
    return items


def daily_candidates(env, keyword_index, hits=10):
    """その日のキーワードで候補を取得する。keyword_indexは0始まりの通し番号（例：経過日数）"""
    keyword = KEYWORDS[keyword_index % len(KEYWORDS)]
    return keyword, search_items(env, keyword, hits=hits)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    from load_env import load_env
    env = load_env()
    kw, items = daily_candidates(env, keyword_index=0)
    print(f"keyword={kw} / {len(items)} items")
    for it in items[:5]:
        print(f" - [{it['review_count']}件] {it['name'][:40]} ({it['price']}円)")
