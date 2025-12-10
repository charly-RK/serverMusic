from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app

# Configuration
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

@app.route('/search', methods=['POST'])
def search_videos():
    """Search YouTube videos"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)
            
            videos = []
            for entry in search_results.get('entries', []):
                video_id = entry.get('id', '')
                video_url = entry.get('webpage_url', f"https://www.youtube.com/watch?v={video_id}")
                
                print(f"DEBUG - Video ID: {video_id}, URL: {video_url}")
                
                videos.append({
                    'id': video_id,
                    'title': entry.get('title', ''),
                    'url': video_url,
                    'thumbnail': entry.get('thumbnail', ''),
                    'duration': entry.get('duration', 0),
                    'author': entry.get('uploader', ''),
                })
            
            return jsonify({'results': videos})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    """Download YouTube video as MP3"""
    try:
        data = request.json
        video_id = data.get('video_id', '')
        title = data.get('title', 'audio')
        
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        # Sanitize filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        output_path = DOWNLOAD_DIR / f"{safe_title}.mp3"
        
        # yt-dlp options for MP3 download
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': str(DOWNLOAD_DIR / f"{safe_title}.%(ext)s"),
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [lambda d: print(f"Progress: {d.get('_percent_str', '0%')}")],
            'ffmpeg_location': 'C:\\ffmpeg\\bin',  # Specify FFmpeg location
        }
        
        # Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        
        # Check if file exists
        if output_path.exists():
            return jsonify({
                'success': True,
                'file_path': f"{safe_title}.mp3",  # Return only filename
                'file_size': output_path.stat().st_size
            })
        else:
            return jsonify({'error': 'Download failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_file/<path:filename>', methods=['GET'])
def download_file(filename):
    """Serve downloaded MP3 file with streaming"""
    try:
        file_path = DOWNLOAD_DIR / filename
        if file_path.exists():
            def generate():
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)  # Read in 8KB chunks
                        if not chunk:
                            break
                        yield chunk
            
            from flask import Response
            return Response(
                generate(),
                mimetype='audio/mpeg',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Length': str(file_path.stat().st_size)
                }
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"Error serving file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

if __name__ == '__main__':
    print("🚀 YouTube Download Server Starting...")
    print(f"📁 Download directory: {DOWNLOAD_DIR.absolute()}")
    port = int(os.environ.get('PORT', 5001))
    print(f"🌐 Server running on http://0.0.0.0:{port}")
    print("💡 Use your PC's IP address to connect from Flutter app")
    app.run(host='0.0.0.0', port=port, debug=False)
