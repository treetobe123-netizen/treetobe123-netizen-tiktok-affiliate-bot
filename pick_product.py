"""その日のキーワードで楽天商品を1件選び、JSONを標準出力に書き出すCLI

「マタイガジェット部」向け：ガジェット・便利家電系キーワードを日替わりでローテーション。

使い方:
  python pick_product.py            # 日付ローテーションでキーワードを自動選択
  python pick_product.py --keyword "モバイルバッテリー 大容量"   # キーワード指定
"""
import argparse
import datetime
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

from load_env import load_env
from rakuten_research import KEYWORDS, search_items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", help="指定があればこのキーワードで検索する(省略時は日付ローテーション)")
    parser.add_argument("--hits", type=int, default=10)
    args = parser.parse_args()

    env = load_env()
    if args.keyword:
        keyword = args.keyword
    else:
        day_index = datetime.date.today().toordinal()
        keyword = KEYWORDS[day_index % len(KEYWORDS)]

    items = search_items(env, keyword, hits=args.hits)
    if not items:
        print(json.dumps({"error": f"'{keyword}' で商品が見つかりませんでした"}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({"keyword": keyword, "item": items[0]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
