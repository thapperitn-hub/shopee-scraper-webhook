import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

def scrape_shopee(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        # ดึงหน้าเว็บจาก Shopee
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. ดึงชื่อสินค้าจาก Open Graph Title หรือ <title>
        title = None
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        else:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.strip()

        # ลบคำว่า | Shopee Thailand ออกถ้ามี
        if title:
            title = re.sub(r"\s*\|\s*Shopee.*$", "", title, flags=re.IGNORECASE)

        # 2. ดึงรูปภาพสินค้าจาก Open Graph Image
        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image_url = og_image["content"].strip()

        return title or "ไม่พบชื่อสินค้า", image_url or ""

    except Exception as e:
        print(f"Scraping error: {e}")
        return "เกิดข้อผิดพลาดในการดึงข้อมูล", ""

@app.route('/', methods=['POST'])
def scrape():
    data = request.get_json() or {}
    product_url = data.get('url')

    if not product_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    title, image_url = scrape_shopee(product_url)

    return jsonify({
        "status": "success",
        "title": title,
        "image_url": image_url
    })

if __name__ == '__main__':
    app.run()
