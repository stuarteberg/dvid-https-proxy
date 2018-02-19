"""
Demonstrates a simple flask server that:

  1. Serves static files over https (anything dropped into the 'static-files' directory)
  2. Any requests that begin with 'dvid-proxy' are automatically streamed from emdata3:8000 to the client, but over https.

To use this demo server:

# Install pre-requisites (flask, requests)
conda install python=3 flask requests

# Generate key files.
# For this demo, I assume they live in this same directory.
cd /path/to/this/code
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

# Launch the server.
python dvid-https-proxy.py
"""

import os
import requests
from flask import Flask, request, send_from_directory, redirect, stream_with_context, Response, url_for

import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'key.pem')

app = Flask(__name__, static_url_path='')

@app.route('/static-files/<path:path>')
def send_static_file(path):
    return send_from_directory('static-files', path)

@app.route('/')
def index():
    # Using redirect here might be bad style instead of serving the data directly.
    return redirect('/static-files/html/static-index.html')

@app.route('/dvid-proxy/<path:dvid_endpoint>')
def stream_from_dvid(dvid_endpoint):
    url = 'http://emdata3:8000/' + dvid_endpoint
    req = requests.get(url, stream=True)
    return Response( stream_with_context(req.iter_content()),
                     content_type=req.headers['content-type'] )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4443,  debug=True, ssl_context=context)
