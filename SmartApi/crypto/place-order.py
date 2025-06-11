import hashlib
import hmac
import json
import time
import requests


def place_order(api_key, api_secret, product_id, size, order_type, side):
    """
    Places an order on the DeltaEx exchange.

    Args:
        api_key (str): Your API key.
        api_secret (str): Your API secret.
        product_id (int): Product ID (e.g., 27 for BTCUSD).
        size (int): Order size.
        order_type (str): Type of order (e.g., 'market_order').
        side (str): Order side ('buy' or 'sell').

    Returns:
        dict: The response from the API.
    """

    def generate_signature(method, endpoint, payload, secret):
        timestamp = str(int(time.time()))
        signature_data = method + timestamp + endpoint + payload
        message = bytes(signature_data, 'utf-8')
        secret_bytes = bytes(secret, 'utf-8')
        hash_obj = hmac.new(secret_bytes, message, hashlib.sha256)
        return hash_obj.hexdigest(), timestamp

    # Prepare order data
    order_data = {
        'product_id': product_id,
        'size': size,
        'order_type': order_type,
        'side': side,
        'leverage': 100
    }
    body = json.dumps(order_data, separators=(',', ':'))
    method = 'POST'
    endpoint = '/v2/orders'

    # Generate signature
    signature, timestamp = generate_signature(method, endpoint, body, api_secret)

    # Request headers
    headers = {
        'api-key': api_key,
        'signature': signature,
        'timestamp': timestamp,
        'Content-Type': 'application/json'
    }

    # Send request
    response = requests.post(f'https://cdn.india.deltaex.org{endpoint}', headers=headers, data=body)

    # Handle response
    if response.status_code == 200:
        return response.json()
    else:
        return {'success': False, 'error': response.text, 'status_code': response.status_code}


# Example usage
if __name__ == "__main__":
    api_key = '0aEo4GqtpgG0XDxwfQtlMrmgYbXFXy'
    api_secret = 'hVLfoPteMA9pfty3vMJaRwADwBcpSPY57ab3GhhaM3wOZssRtoFs0f3AOoft'
    result = place_order(api_key, api_secret, product_id=65412, size=10, order_type='market_order', side='sell')
    print(result)
