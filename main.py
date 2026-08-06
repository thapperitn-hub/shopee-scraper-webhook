from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def scrape():
    data = request.get_json()
    product_url = data.get('url')
    
    # โค้ดดึงข้อมูล Shopee ของคุณที่นี่...
    return jsonify({
        "status": "success",
        "title": "ชื่อสินค้าที่ดึงได้",
        "image_url": "ลิงก์รูปภาพ"
    })

if __name__ == '__main__':
    app.run()
