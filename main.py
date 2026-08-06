import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

# ใช้ API Key จาก ScraperAPI ของคุณ
SCRAPER_API_KEY = "c4909b3027fb87a7adf7d9d1ba8cc674"

def scrape_tiktok(url):
    try:
        # ยิงผ่าน ScraperAPI แบบ render=true เพื่อจำลองการเปิดหน้าเว็บจริง
        payload = {
            'api_key': SCRAPER_API_KEY,
            'url': url,
            'render': 'true'
        }
        response = requests.get('http://api.scraperapi.com', params=payload, timeout=35)
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. แกะชื่อสินค้าจริงจาก og:title หรือ og:description
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        else:
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                title = og_desc["content"].strip()

        # 2. แกะรูปภาพจริงจาก og:image
        image_url = ""
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
