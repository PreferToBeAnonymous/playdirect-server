from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "PlayDirect Server is Running! 🚀"})

@app.route('/get-video', methods=['GET'])
def get_video_url():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400

    print(f"Processing URL: {video_url}")
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'forceurl': True, 
            'noplaylist': True,
            'cookiefile': 'cookies.txt', # Cookies for auth
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'web'],
                    'player_skip': ['webpage', 'configs', 'js'],
                    'include_ssl_logs': False
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url', None)
            title = info.get('title', 'Video')

            if download_url:
                # Hum Direct URL nahi denge, balki Proxy URL denge
                return jsonify({
                    'success': True,
                    'title': title,
                    'download_url': download_url, # Original URL (for reference)
                    'proxy': True # Flag to tell App to use proxy
                })
            else:
                return jsonify({'success': False, 'error': 'Could not extract link'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 👇 NEW: Video Streamer (Proxy) 👇
@app.route('/stream-video', methods=['GET'])
def stream_video():
    video_url = request.args.get('url')
    try:
        # Server khud video layega aur App ko pass karega
        req = requests.get(video_url, stream=True)
        return Response(stream_with_context(req.iter_content(chunk_size=1024)), 
                        content_type=req.headers['content-type'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)