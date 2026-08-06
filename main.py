import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

# API Key จาก ScraperAPI ของคุณ
SCRAPER_API_KEY = "c4909b3027fb87a7adf7d9d1ba8cc674"

def get_shopee_data_via_scraperapi(product_url):
    try:
        # ส่ง Request ผ่าน Proxy ของ ScraperAPI
        payload = {
            'api_key': SCRAPER_API_KEY,
            'url': product_url,
            'render': 'true'  # ให้ ScraperAPI โหลด JavaScript ของ Shopee จนสมบูรณ์
        }
        
        response = requests.get('http://api.scraperapi.com', params=payload, timeout=60)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. ดึงชื่อสินค้า
        title = None
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        else:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.strip()

        if title:
            title = re.sub(r"\s*\|\s*Shopee.*$", "", title, flags=re.IGNORECASE)

        # 2. ดึงรูปภาพสินค้า
        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image_url = og_image["content"].strip()

        return title or "ไม่พบชื่อสินค้า", image_url or ""

    except Exception as e:
        print(f"Error scraping with ScraperAPI: {e}")
        return None, None

@app.route('/', methods=['POST'])
def scrape():
    req_data = request.get_json() or {}
    product_url = req_data.get('url')

    if not product_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    title, image_url = get_shopee_data_via_scraperapi(product_url)

    if title and title != "ไม่พบชื่อสินค้า":
        return jsonify({
            "status": "success",
            "title": title,
            "image_url": image_url
        })
    else:
        return jsonify({"status": "error", "message": "Failed to scrape Shopee data"}), 500

if __name__ == '__main__':
    app.run()
