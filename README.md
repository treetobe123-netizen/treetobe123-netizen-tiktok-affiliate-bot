# tiktok-affiliate-bot

TikTok向け楽天アフィリエイト自動投稿bot。instagram-affiliate-botと同じ楽天商品ローテーション方式。

## 仕組み(2段階のバトンリレー)

Instagramと違い、TikTokへの投稿自体もHiggsFieldのMCPツール(`tiktok_publish`系)でクラウドルーティンから直接行えるため、GitHub Actionsでの投稿ステップが不要:

1. **GitHub Actions `pick-product.yml`**（毎日12:36 JST、secrets利用）: `pick_product.py` で今日の楽天商品を選び `queue/today_item.json` に書いてpush
2. **クラウドルーティン**「AIカンパニー TikTok動画生成+投稿(HiggsField)」: `higgsfield_daily_prompt.md` の指示に従い、HiggsFieldで縦型ショート動画を生成し、そのままTikTokに投稿。`log.jsonl`に記録し、`threads-hub/tiktok/index.html`（プロフィールリンク先の固定ページ）も更新してpush

必要なGitHub repo secrets: `RAKUTEN_APPLICATION_ID` / `RAKUTEN_AFFILIATE_ID` / `RAKUTEN_ACCESS_KEY` / `RAKUTEN_PROXY_URL` / `RAKUTEN_PROXY_SECRET`（instagram-affiliate-botと同じ値）

## 導線

TikTokの説明欄はURLをクリックできないため、プロフィールのリンク欄を
`https://treetobe123-netizen.github.io/threads-hub/tiktok/` に**1回だけ手動設定**しておき、
このページの中身（今日のおすすめ商品と実際のリンク）を投稿のたびに自動更新する。
