# queue/

自動化のバトンリレー用フォルダ。中身は自動生成・自動削除されるので通常は空。

- `today_item.json` — GitHub Actions（pick-product.yml）が書く、今日選ばれた商品

Instagram部署と違い、TikTokは投稿自体もクラウドルーティン側（HiggsField MCP）で完結するため、
`ready_to_post.json` のような2段目のファイルは無い。詳しくは `../higgsfield_daily_prompt.md` と
`.github/workflows/` を参照。
