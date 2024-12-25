from flask import Flask, send_file, jsonify, request
import requests
import ssl
import socket
import netifaces

app = Flask(__name__)

def get_ip():
    try:
        # Get all network interfaces and their addresses
        addresses = []
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:  # IPv4 addresses
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):  # Skip localhost
                        addresses.append({
                            'interface': interface,
                            'ip': ip
                        })
        return {
            'hostname': socket.gethostname(),
            'interfaces': addresses
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/api/geocode', methods=['GET'])
def geocode():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'No city provided'}), 400
    
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
    headers = {'User-Agent': 'AntipodeMapper/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return jsonify({'error': 'City not found'}), 404
            
        location = data[0]
        return jsonify({
            'lat': float(location['lat']),
            'lon': float(location['lon']),
            'display_name': location['display_name']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug')
def debug():
    network_info = get_ip()
    client_info = {
        'remote_addr': request.remote_addr,
        'headers': dict(request.headers)
    }
    return jsonify({
        'network': network_info,
        'client': client_info
    })

if __name__ == '__main__':
    # Print network information on startup
    network_info = get_ip()
    print("\n=== Server Network Information ===")
    print(f"Hostname: {network_info.get('hostname')}")
    print("\nAvailable Interfaces:")
    for interface in network_info.get('interfaces', []):
        print(f"Interface: {interface['interface']} - IP: {interface['ip']}")
    
    print("\nTry connecting to:")
    print(f"https://192.168.1.3:5000 (Your local network IP)")
    print(f"https://localhost:5000 (Local testing)")
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    app.run(debug=True, host='0.0.0.0', ssl_context=context, port=5000) 