from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)

DATABASE = []

@app.route('/api/generate-batch', methods=['GET'])
def generate_batch_keys():
    generated = []
    types = ["1day", "1week", "1month"]
    
    for t in types:
        for _ in range(20):
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            key_code = f"PATRON-{t.upper()}-{random_str}"
            
            key_data = {
                "key": key_code,
                "type": t,
                "status": "unused",
                "hwid": None,
                "expires_at": None
            }
            DATABASE.append(key_data)
            generated.append(key_code)
            
    return jsonify({"status": "success", "keys": generated})

@app.route('/api/verify', methods=['POST'])
def verify_key():
    data = request.json
    entered_key = data.get('key')
    device_hwid = data.get('hwid')
    
    target_key = None
    for k in DATABASE:
        if k['key'] == entered_key:
            target_key = k
            break
            
    if not target_key:
        return jsonify({"status": "invalid", "message": "Invalid license key."})
        
    now = datetime.now()
    
    if target_key['status'] == 'unused':
        target_key['hwid'] = device_hwid
        target_key['status'] = 'active'
        
        if target_key['type'] == '1day':
            target_key['expires_at'] = now + timedelta(days=1)
        elif target_key['type'] == '1week':
            target_key['expires_at'] = now + timedelta(weeks=1)
        elif target_key['type'] == '1month':
            target_key['expires_at'] = now + timedelta(days=30)
            
        return jsonify({"status": "success", "message": "Activated successfully!"})
        
    if target_key['hwid'] != device_hwid:
        return jsonify({"status": "error", "message": "This key is bound to another device!"})
        
    if now > target_key['expires_at']:
        target_key['status'] = 'expired'
        return jsonify({"status": "expired", "message": "License key has expired."})
        
    return jsonify({"status": "success", "message": "Valid key."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
