import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

def scrape_tiktok(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        # ดึงหน้าเว็บ TikTok (รองรับทั้งลิงก์ย่อ vt.tiktok.com และลิงก์เต็ม)
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. ดึงชื่อคลิป/ชื่อสินค้าจาก og:title หรือ og:description
        title = None
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        else:
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                title = og_desc["content"].strip()

        # 2. ดึงรูปปกคลิป/รูปสินค้าจาก og:image
        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image_url = og_image["content"].strip()

        return title or "คลิปสินค้า TikTok", image_url or ""

    except Exception as e:
        print(f"TikTok Scraping Error: {e}")
        return "คลิปสินค้า TikTok", ""

@app.route('/', methods=['POST'])
def scrape():
    data = request.get_json() or {}
    tiktok_url = data.get('url')

    if not tiktok_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    title, image_url = scrape_tiktok(tiktok_url)

    return jsonify({
        "status": "success",
        "title": title,
        "image_url": image_url
    })

if __name__ == '__main__':
    app.run()
