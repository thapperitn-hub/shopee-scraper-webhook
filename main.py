import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

SCRAPER_API_KEY = "c4909b3027fb87a7adf7d9d1ba8cc674"

def get_shopee_data(product_url):
    try:
        # 1. แตกชื่อสินค้าและรูปภาพเบื้องต้นจาก OpenGraph
        payload = {
            'api_key': SCRAPER_API_KEY,
            'url': product_url,
            'render': 'false', # ปิด render เพื่อลดความช้าและป้องกัน timeout
            'country_code': 'th'
        }
        
        response = requests.get('https://api.scraperapi.com', params=payload, timeout=30)
        
        # รองรับกรณีลิงก์ย่อโดน Redirect
        soup = BeautifulSoup(response.text, 'html.parser')

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

        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image_url = og_image["content"].strip()

        return title or "สินค้า Shopee", image_url or ""

    except Exception as e:
        print(f"Error scraping: {e}")
        return "สินค้า Shopee", ""

@app.route('/', methods=['POST'])
def scrape():
    req_data = request.get_json() or {}
    product_url = req_data.get('url')

    if not product_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    title, image_url = get_shopee_data(product_url)

    return jsonify({
        "status": "success",
        "title": title,
        "image_url": image_url
    })

if __name__ == '__main__':
    app.run()
