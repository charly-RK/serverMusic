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

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({'message': 'YouTube Download API', 'status': 'running'})

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

@app.route('/search_albums', methods=['POST'])
def search_albums():
    """Search YouTube albums/playlists (official only)"""
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
        
        albums = []
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Strategy 1: Search for "Artist - Topic" channel which has official albums
            try:
                topic_query = f"ytsearch5:{query} topic albums"
                print(f"Searching with query: {topic_query}")
                search_results = ydl.extract_info(topic_query, download=False)
                
                if search_results and 'entries' in search_results:
                    for entry in search_results.get('entries', []):
                        if not entry:
                            continue
                        
                        # Check if this is a playlist/album
                        url = entry.get('url', '')
                        webpage_url = entry.get('webpage_url', '')
                        
                        # If it's a playlist URL, extract it
                        if 'playlist' in url or 'playlist' in webpage_url:
                            try:
                                playlist_url = webpage_url if 'playlist' in webpage_url else url
                                playlist_info = ydl.extract_info(playlist_url, download=False)
                                
                                if playlist_info:
                                    playlist_id = playlist_info.get('id', '')
                                    title = playlist_info.get('title', '')
                                    uploader = playlist_info.get('uploader', '') or playlist_info.get('channel', '')
                                    
                                    # Get thumbnail
                                    thumbnail = ''
                                    if 'thumbnail' in playlist_info:
                                        thumbnail = playlist_info['thumbnail']
                                    elif 'thumbnails' in playlist_info and len(playlist_info['thumbnails']) > 0:
                                        thumbnail = playlist_info['thumbnails'][-1].get('url', '')
                                    
                                    # Get track count
                                    track_count = len(playlist_info.get('entries', []))
                                    
                                    if playlist_id and title and track_count > 0:
                                        print(f"Found album: {title} by {uploader} ({track_count} tracks)")
                                        albums.append({
                                            'id': playlist_id,
                                            'title': title,
                                            'thumbnail': thumbnail,
                                            'author': uploader,
                                            'track_count': track_count,
                                        })
                            except Exception as e:
                                print(f"Error extracting playlist: {e}")
                                continue
            except Exception as e:
                print(f"Error in topic search: {e}")
            
            # Strategy 2: Direct search for album playlists
            if len(albums) < 3:
                try:
                    album_query = f"ytsearch10:{query} full album playlist"
                    print(f"Searching with query: {album_query}")
                    search_results = ydl.extract_info(album_query, download=False)
                    
                    if search_results and 'entries' in search_results:
                        for entry in search_results.get('entries', []):
                            if not entry:
                                continue
                            
                            # Check if video title suggests it's an album
                            title = entry.get('title', '').lower()
                            if 'full album' in title or 'álbum completo' in title or 'album completo' in title:
                                video_id = entry.get('id', '')
                                video_title = entry.get('title', '')
                                uploader = entry.get('uploader', '') or entry.get('channel', '')
                                thumbnail = entry.get('thumbnail', '')
                                
                                if video_id and video_title:
                                    print(f"Found album video: {video_title} by {uploader}")
                                    # Use video as single-track "album"
                                    albums.append({
                                        'id': video_id,
                                        'title': video_title,
                                        'thumbnail': thumbnail,
                                        'author': uploader,
                                        'track_count': 1,
                                    })
                                    
                                    if len(albums) >= 5:
                                        break
                except Exception as e:
                    print(f"Error in album search: {e}")
            
            print(f"Returning {len(albums)} albums")
            return jsonify({'results': albums})
    
    except Exception as e:
        print(f"Error in search_albums: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/album_tracks', methods=['POST'])
def get_album_tracks():
    """Get tracks from a YouTube album/playlist"""
    try:
        data = request.json
        playlist_id = data.get('playlist_id', '')
        
        if not playlist_id:
            return jsonify({'error': 'Playlist ID is required'}), 400
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            tracks = []
            for entry in playlist_info.get('entries', []):
                if entry:
                    tracks.append({
                        'id': entry.get('id', ''),
                        'title': entry.get('title', ''),
                        'url': entry.get('url', f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                        'thumbnail': entry.get('thumbnail', ''),
                        'duration': entry.get('duration', 0),
                        'author': entry.get('uploader', ''),
                    })
            
            return jsonify({'tracks': tracks})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_album', methods=['POST'])
def download_album():
    """Download entire album into a dedicated folder"""
    try:
        data = request.json
        playlist_id = data.get('playlist_id', '')
        album_title = data.get('album_title', 'Album')
        
        if not playlist_id:
            return jsonify({'error': 'Playlist ID is required'}), 400
        
        # Sanitize album name for folder
        safe_album_name = "".join(c for c in album_title if c.isalnum() or c in (' ', '-', '_')).strip()
        album_folder = DOWNLOAD_DIR / safe_album_name
        album_folder.mkdir(exist_ok=True)
        
        # Get playlist tracks
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            downloaded_files = []
            total_tracks = len(playlist_info.get('entries', []))
            
            # Download each track
            for idx, entry in enumerate(playlist_info.get('entries', []), 1):
                if entry:
                    video_id = entry.get('id', '')
                    title = entry.get('title', f'Track {idx}')
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    output_path = album_folder / f"{safe_title}.mp3"
                    
                    # Download options
                    download_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '320',
                        }],
                        'outtmpl': str(album_folder / f"{safe_title}.%(ext)s"),
                        'quiet': False,
                        'no_warnings': False,
                    }
                    
                    try:
                        with yt_dlp.YoutubeDL(download_opts) as download_ydl:
                            download_ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                        
                        if output_path.exists():
                            downloaded_files.append({
                                'title': title,
                                'file_path': f"{safe_album_name}/{safe_title}.mp3",
                                'progress': f"{idx}/{total_tracks}"
                            })
                    except Exception as e:
                        print(f"Error downloading {title}: {e}")
                        continue
            
            return jsonify({
                'success': True,
                'album_folder': safe_album_name,
                'downloaded_files': downloaded_files,
                'total_tracks': total_tracks
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

if __name__ == '__main__':
    print("YouTube Download Server Starting...")
    print(f"Download directory: {DOWNLOAD_DIR.absolute()}")
    port = int(os.environ.get('PORT', 5001))
    print(f"Server running on http://0.0.0.0:{port}")
    print("Use your PC's IP address to connect from Flutter app")
    app.run(host='0.0.0.0', port=port, debug=False)
