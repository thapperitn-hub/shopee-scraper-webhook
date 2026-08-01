import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/get-shopee-media", methods=["POST"])
def get_shopee_media():
    try:
        data = request.get_json()
        raw_url = data.get("url")

        if not raw_url:
            return jsonify({"status": "error", "message": "No URL provided"}), 400

        # 1. แกะลิงก์ย่อ Affiliate ให้เป็น URL สินค้าเต็ม
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    " AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )

        res = session.get(raw_url, allow_redirects=True)
        full_url = res.url

        # 2. สกัด shop_id และ item_id จาก URL สินค้า
        if "/product/" in full_url:
            path_part = full_url.split("/product/")[1].split("?")[0]
            parts = path_part.strip("/").split("/")
            shop_id, item_id = parts[0], parts[1]
        elif "item_id=" in full_url and "shop_id=" in full_url:
            params = full_url.split("?")[1].split("&")
            param_dict = dict(p.split("=") for p in params if "=" in p)
            shop_id = param_dict.get("shop_id")
            item_id = param_dict.get("item_id")
        else:
            return (
                jsonify(
                    {"status": "error", "message": "Invalid Shopee URL structure"}
                ),
                400,
            )

        # 3. ยิงขอข้อมูลจาก Shopee Internal API
        api_url = f"https://shopee.co.th/api/v4/pdp/get_pc?shop_id={shop_id}&item_id={item_id}"
        api_res = session.get(api_url).json()

        item = api_res.get("data", {}).get("item", {})

        # 4. แปลงรูปภาพทั้งหมดเป็นลิงก์ CDN
        raw_images = item.get("images", [])
        image_urls = [
            f"https://down-th.img.susercontent.com/file/{img_id}"
            for img_id in raw_images
        ]

        # 5. สกัดเอาลิงก์วิดีโอ (.mp4)
        video_url = None
        video_info = item.get("video_info_list", [])
        if video_info:
            video_url = video_info[0].get("default_format", {}).get("url")

        return jsonify(
            {
                "status": "success",
                "title": item.get("title"),
                "video_url": video_url,
                "images": image_urls,
                "main_image": image_urls[0] if image_urls else None,
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)