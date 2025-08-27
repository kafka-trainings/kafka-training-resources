from flask import Flask, jsonify
import requests
from config import PRODUCT_SERVICE_URL, PRICE_SERVICE_URL, WEBSHOP_SERVICE_PORT

app = Flask(__name__)

def fetch_products():
    resp = requests.get(f'{PRODUCT_SERVICE_URL}/products', timeout=5)
    if resp.status_code != 200:
        raise Exception("Product service unavailable")
    return resp.json()

def fetch_price(product_id):
    resp = requests.get(f'{PRICE_SERVICE_URL}/prices/{product_id}', timeout=5)
    if resp.status_code != 200:
        raise Exception(f"Price service unavailable for product {product_id}")
    return resp.json().get('price')

@app.route('/products')
def get_products():
    products = fetch_products()
    for p in products:
        p['price'] = fetch_price(p['id'])
        p.pop('internal_sku', None)  # Remove internal info
    return jsonify(products)

@app.route('/products/<int:product_id>')
def get_product(product_id):
    try:
        resp = requests.get(f'{PRODUCT_SERVICE_URL}/products/{product_id}', timeout=5)
        if resp.status_code != 200:
            return ('', 404)
        product = resp.json()
        product['price'] = fetch_price(product_id)
        product.pop('internal_sku', None)  # Remove internal info
        return jsonify(product)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=WEBSHOP_SERVICE_PORT)