"""ローカルPC(Windowsタスクスケジューラ)で毎日実行する動画生成+キュー登録スクリプト

HiggsFieldの動画生成が有料プラン必須になったため、ローカルのComfyUI(LTX-2.5)で
動画生成する。投稿自体(TikTok publish)はHiggsField MCPでしかできないため、
ここでは「動画生成→公開URL化→queue/ready_to_post.jsonに書く」までを担当し、
続きはクラウドルーティンがHiggsFieldのmedia_import_url経由で拾って投稿する。

前提: ComfyUIが http://127.0.0.1:8188 で起動していること

使い方:
  python generate_daily_post.py
"""
import datetime
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

from load_env import load_env
from generate_media import generate_video_ltx
from publish_media import publish_to_github_pages
from caption_templates import build_template_caption

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_TODAY = os.path.join(BASE_DIR, "queue", "today_item.json")
QUEUE_READY = os.path.join(BASE_DIR, "queue", "ready_to_post.json")


def build_prompt(item):
    kw = item.get("keyword", "gadget")
    return (
        f"Studio product commercial: a {kw} product on a clean white background, "
        "camera slowly orbits and pushes in, soft even studio lighting, sharp reflective "
        "surfaces, minimal and modern tech aesthetic, no text, no logo, no people, no watermark"
    )


def git(*args, cwd=BASE_DIR):
    subprocess.run(["git", *args], cwd=cwd, check=True)


def git_push_with_retry(max_retries=5):
    """クラウドルーティン側のlog.jsonlコミット等との競合に備え、
    pull --rebase→push をリトライする"""
    for attempt in range(max_retries):
        subprocess.run(["git", "pull", "--rebase"], cwd=BASE_DIR, check=True)
        result = subprocess.run(["git", "push"], cwd=BASE_DIR)
        if result.returncode == 0:
            return
    raise RuntimeError(f"tiktok-affiliate-botへのpushが{max_retries}回失敗しました")


def main():
    subprocess.run(["git", "pull"], cwd=BASE_DIR, check=True)

    if not os.path.exists(QUEUE_TODAY):
        print("今日はまだ queue/today_item.json がありません。何もせず終了します。")
        return

    with open(QUEUE_TODAY, encoding="utf-8") as f:
        today = json.load(f)
    item = today["item"]

    env = load_env()

    print(f"動画生成中(ComfyUI/LTX-2.5): {item['name'][:40]}...")
    prompt = build_prompt(item)
    local_path = generate_video_ltx(prompt, duration=5)[0]
    print(f"生成完了: {local_path}")

    public_url = publish_to_github_pages(env, local_path)
    print(f"公開URL: {public_url}")

    caption = build_template_caption(item)

    ready = {
        "video_url": public_url,
        "caption": caption,
        "item": item,
    }
    with open(QUEUE_READY, "w", encoding="utf-8") as f:
        json.dump(ready, f, ensure_ascii=False, indent=2)

    os.remove(QUEUE_TODAY)

    git("add", "queue/ready_to_post.json", "queue/today_item.json")
    git("commit", "-m", f"queue: video ready to post {datetime.date.today().isoformat()} (local ComfyUI)")
    git_push_with_retry()
    print("push完了。クラウドルーティンがHiggsFieldに取り込んでTikTokに投稿します。")


if __name__ == "__main__":
    main()
