import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_shop_and_item_id(url):
    """สกัด shop_id และ item_id จาก URL Shopee"""
    # 1. แพตเทิร์นสำหรับ /product/shop_id/item_id
    match = re.search(r'product/(\d+)/(\d+)', url)
    if match:
        return match.group(1), match.group(2)
        
    # 2. แพตเทิร์นสำหรับ i.shop_id.item_id
    match = re.search(r'i\.(\d+)\.(\d+)', url)
    if match:
        return match.group(1), match.group(2)
    
    # 3. แพตเทิร์นสำหรับ /username/shop_id/item_id
    match = re.search(r'/[^/]+?/(\d+)/(\d+)', url)
    if match:
        return match.group(1), match.group(2)
        
    return None, None

@app.route('/get-shopee-media', methods=['POST'])
def get_shopee_media():
    try:
        data = request.get_json() or {}
        clean_url = str(data.get('url', '')).strip("'\" ")
        
        if not clean_url:
            return jsonify({'status': 'error', 'message': 'URL is required'}), 400

        # สกัด shop_id และ item_id จาก URL ตรงๆ
        shop_id, item_id = extract_shop_and_item_id(clean_url)
        
        if not shop_id or not item_id:
            return jsonify({
                'status': 'error', 
                'message': f'Could not extract shop_id/item_id. Please use full product URL: {clean_url}'
            }), 400

        # ยิงตรงไปที่ Shopee Internal PDP API
        api_url = f"https://shopee.co.th/api/v4/pdp/get_pc?itemid={item_id}&shopid={shop_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': clean_url
        }
        
        res = requests.get(api_url, headers=headers, timeout=10)
        res_json = res.json()
        
        item_data = res_json.get('data', {})
        if not item_data:
            return jsonify({'status': 'error', 'message': 'Failed to fetch item data from Shopee API'}), 400

        # สกัดรูปภาพทั้งหมด
        raw_images = item_data.get('images', [])
        images = [f"https://down-th.img.susercontent.com/file/{img}" for img in raw_images]
        main_image = images[0] if images else ""

        # สกัดวิดีโอ (ถ้ามี)
        video_url = ""
        video_info_list = item_data.get('video_info_list', [])
        if video_info_list and len(video_info_list) > 0:
            default_video = video_info_list[0].get('default_format', {})
            video_url = default_video.get('url', '')

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
