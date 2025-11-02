from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def extract_token(hubcloud_url):
    file_id = hubcloud_url.strip().split('/')[-1]
    token_url = f"https://gamerxyt.com/hubcloud.php?host=hubcloud&id={file_id}"
    r = requests.get(token_url)
    token_match = re.search(r'token=([a-zA-Z0-9+/=]+)', r.text)
    if token_match:
        token = token_match.group(1)
        return file_id, token
    return None, None

def extract_hubcloud_links(file_id, token):
    final_url = f"https://gamerxyt.com/hubcloud.php?host=hubcloud&id={file_id}&token={token}"
    r = requests.get(final_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = {}

    def find_link(pattern, label):
        tag = soup.find('a', href=re.compile(pattern))
        if tag:
            links[label] = tag['href']

    find_link(r'hubcloud.host/download', 'hubcloud')
    find_link(r'pixeldrain', 'pixeldrain')
    find_link(r'fsl\.gigabytes\.click', 'fslv2')
    find_link(r'say-no-to-piracy', 'fsl_alt')
    find_link(r'mega\.nz', 'mega')
    find_link(r'zipdisk', 'zipdisk')

    return links

def extract_vcloud_links(vcloud_url):
    r = requests.get(vcloud_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = {}

    def find_link(pattern, label):
        tag = soup.find('a', href=re.compile(pattern))
        if tag:
            links[label] = tag['href']

    find_link(r'pixeldrain', 'pixeldrain')
    find_link(r'fsl\.gigabytes\.click', 'fslv2')
    find_link(r'say-no-to-piracy', 'fsl_alt')
    find_link(r'mega\.nz', 'mega')
    find_link(r'zipdisk', 'zipdisk')

    return links

@app.route('/extract', methods=['POST'])
def extract():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    if 'hubcloud.fit' in url:
        file_id, token = extract_token(url)
        if not token:
            return jsonify({'error': 'Token extraction failed'}), 500
        links = extract_hubcloud_links(file_id, token)
        return jsonify({'type': 'hubcloud', 'file_id': file_id, 'token': token, 'links': links})

    elif 'vcloud' in url or 'oxxfile' in url:
        links = extract_vcloud_links(url)
        return jsonify({'type': 'vcloud', 'links': links})

    else:
        return jsonify({'error': 'Unsupported link type'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
