"""生成したメディアファイルをtiktok-hub(GitHub Pages)にpushして公開URLを得るモジュール

HiggsFieldのmedia_import_url/tiktok_publishはpublicなURLを要求するため、
instagram-affiliate-bot側と同じ「専用リポジトリにpush→GitHub Pagesで公開」の
仕組みを流用する(マタイガジェット部は独立ブランドのため、threads-hubではなく
tiktok-hubという別リポジトリを使う)。
"""
import subprocess
import shutil
import os
import time

REPO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok-hub")
MEDIA_DIR = os.path.join(REPO_DIR, "media")


def publish_to_github_pages(env, local_file_path, wait_seconds=60):
    """メディアファイルをtiktok-hub/media/にコピーしてpushし、公開URLを返す"""
    os.makedirs(MEDIA_DIR, exist_ok=True)
    filename = os.path.basename(local_file_path)
    shutil.copyfile(local_file_path, os.path.join(MEDIA_DIR, filename))

    subprocess.run(["git", "add", f"media/{filename}"], cwd=REPO_DIR, check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_DIR)
    if diff.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"add media {filename}"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        time.sleep(wait_seconds)  # GitHub Pagesの反映を待つ(publish.pyの中継ページと同様)

    base = env.get("GITHUB_PAGES_URL", "").rstrip("/")
    if not base:
        raise RuntimeError("GITHUB_PAGES_URLが.envに設定されていません")
    return f"{base}/media/{filename}"
