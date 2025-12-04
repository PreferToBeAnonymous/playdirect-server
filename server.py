from flask import Flask, request, jsonify, Response
import yt_dlp
import requests

app = Flask(__name__)

def get_direct_stream_url(video_url):
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'noplaylist': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash'] 
                }
            },
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info.get('url', None), info.get('title', 'Video')
            
    except Exception as e:
        print(f"Error fetching: {e}")
        return None, str(e)

@app.route('/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400

    print(f"Processing URL: {url}")
    
    # 1. Get Direct Link
    download_url, title = get_direct_stream_url(url)
    
    if download_url:
        return jsonify({
            'success': True, 
            'title': title, 
            'download_url': f"{request.host_url}stream-video?url={requests.utils.quote(download_url)}"
        })
    else:
        return jsonify({'success': False, 'error': f'Failed: {title}'}), 500

@app.route('/stream-video', methods=['GET'])
def stream_video():
    video_url = request.args.get('url')
    
    if not video_url:
        return "No URL provided", 400

    try:
        req = requests.get(video_url, stream=True)
        
        headers = {
            'Content-Type': req.headers.get('Content-Type'),
            'Content-Length': req.headers.get('Content-Length')
        }

        return Response(
            req.iter_content(chunk_size=1024*1024), 
            headers=headers,
            direct_passthrough=True
        )
    except Exception as e:
        return f"Stream Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)