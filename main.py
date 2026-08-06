import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_shopee_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://shopee.co.th/"
    }

    try:
        # Resolve short URL if needed
        res = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        final_url = res.url

        # Extract Item ID and Shop ID from URL
        item_match = re.search(r'i\.(\d+)\.(\d+)', final_url) or re.search(r'-i\.(\d+)\.(\d+)', final_url)
        
        if item_match:
            shop_id = item_match.group(1)
            item_id = item_match.group(2)
            
            # Fetch data directly from Shopee's internal API
            api_url = f"https://shopee.co.th/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            api_res = requests.get(api_url, headers=headers, timeout=10)
            
            if api_res.status_code == 200:
                data = api_res.json().get('data', {})
                title = data.get('name')
                image_code = data.get('image')
                image_url = f"https://down-th.img.susercontent.com/file/{image_code}" if image_code else ""
                
                # Extract Video URL if available
                video_url = ""
                video_info = data.get('video_info_list', [])
                if video_info and len(video_info) > 0:
                    video_url = video_info[0].get('default_format', {}).get('url', '')

                return title, image_url, video_url

        # Fallback parsing HTML directly
        title_match = re.search(r'<title>(.*?)</title>', res.text)
        title = title_match.group(1).replace(" | Shopee Thailand", "") if title_match else "ไม่พบชื่อสินค้า"
        return title, "", ""

    except Exception as e:
        print(f"Error scraping: {e}")
        return None, None, None

@app.route('/', methods=['POST'])
def scrape():
    req_data = request.get_json() or {}
    product_url = req_data.get('url')

    if not product_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    title, image_url, video_url = get_shopee_data(product_url)

    if title:
        return jsonify({
            "status": "success",
            "title": title,
            "image_url": image_url or "",
            "video_url": video_url or ""
        })
    else:
        return jsonify({"status": "error", "message": "Failed to scrape Shopee data"}), 500

if __name__ == '__main__':
    app.run()
