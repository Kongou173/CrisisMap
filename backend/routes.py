import requests
from flask import Blueprint, jsonify, request

shelters_bp = Blueprint('shelters', __name__)

# 避難所検索エンドポイント
@shelters_bp.route('/api/shelters', methods=['GET'])
def get_shelters():
    # クエリパラメータで緯度と経度を取得
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    if not latitude or not longitude:
        return jsonify({"error": "Missing latitude or longitude"}), 400
    
    # OpenStreetMap Nominatim APIを使用して避難所を検索
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        "q": "shelter",
        "format": "json",
        "addressdetails": 1,
        "limit": 10,
        "viewbox": f"{float(longitude)-0.1},{float(latitude)+0.1},{float(longitude)+0.1},{float(latitude)-0.1}",
        "bounded": 1
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch shelters"}), 500

    return jsonify(response.json()), 200
