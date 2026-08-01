import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# RapidAPI Key
RAPIDAPI_KEY = "12b3cd86dbmshaad8c3cb7ec303cp17392bjsn904568abd2a8"

def unshorten_url(url):
    """แปลงลิงก์ย่อ Shopee ให้เป็นลิงก์เต็ม"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print(f"Error unshortening URL: {e}")
        return url

@app.route('/get-shopee-media', methods=['POST'])
def get_shopee_media():
    try:
        data = request.get_json() or {}
        raw_url = data.get('url', '')
        
        # 1. ทำความสะอาด URL
        clean_url = str(raw_url).strip("'\" ")
        if clean_url.startswith('ttps://'):
            clean_url = 'h' + clean_url
        elif not clean_url.startswith('http'):
            clean_url = 'https://' + clean_url
            
        if not clean_url:
            return jsonify({'status': 'error', 'message': 'URL is required'}), 400

        # 2. แปลงลิงก์ย่อเป็นลิงก์เต็ม
        full_url = unshorten_url(clean_url)
        
        # 3. ยิง RapidAPI โดยส่ง full_url หน้าสินค้าโดยตรง
        rapidapi_url = "https://shopee-scraper1.p.rapidapi.com/"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "shopee-scraper1.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        payload = {"url": full_url}
        
        res = requests.post(rapidapi_url, json=payload, headers=headers, timeout=15)
        res_json = res.json()
        
        item_data = res_json.get('data', {})
        if not item_data:
            return jsonify({
                'status': 'error', 
                'message': 'Failed to fetch item data via RapidAPI', 
                'raw_response': res_json
            }), 400

        # 4. สกัดรูปภาพทั้งหมด
        raw_images = item_data.get('images', [])
        images = [f"https://down-th.img.susercontent.com/file/{img}" for img in raw_images]
        main_image = images[0] if images else ""

        # 5. สกัดวิดีโอ (ถ้ามี)
        video_url = ""
        video_info_list = item_data.get('video_info_list', [])
        if video_info_list and len(video_info_list) > 0:
            default_video = video_info_list[0].get('default_format', {})
            video_url = default_video.get('url', '')

        # 6. คืนค่า JSON กลับไปให้ Make
        return jsonify({
            'status': 'success',
            'title': item_data.get('title', ''),
            'main_image': main_image,
            'video_url': video_url,
            'images': images
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
