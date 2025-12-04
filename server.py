from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
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
        # 👇 COOKIES ENABLED HERE 👇
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'forceurl': True, 
            'noplaylist': True,
            'cookiefile': 'cookies.txt',  # <--- YEH LINE MAGIC KAREGI
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url', None)
            title = info.get('title', 'Video')

            if download_url:
                print(f"Success: Link extracted for {title}")
                return jsonify({
                    'success': True,
                    'title': title,
                    'download_url': download_url
                })
            else:
                return jsonify({'success': False, 'error': 'Could not extract link'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)