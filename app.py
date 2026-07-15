from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "ytdlp-api running"})

@app.route('/audio')
def audio():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "url required"}), 400
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url')]
            formats.sort(key=lambda x: x.get('abr', 0) or 0, reverse=True)
            best = formats[0] if formats else None
            return jsonify({
                "status": "ok",
                "title": info.get('title'),
                "duration": info.get('duration'),
                "url": best['url'] if best else None
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/video')
def video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "url required"}), 400
    try:
        ydl_opts = {
            'format': 'bestvideo[height<=480][ext=mp4]+bestaudio/best[height<=480]',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url') and (f.get('height') or 999) <= 480]
            formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
            best = formats[0] if formats else None
            return jsonify({
                "status": "ok",
                "title": info.get('title'),
                "duration": info.get('duration'),
                "url": best['url'] if best else None,
                "quality": f"{best.get('height', '?')}p" if best else None
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "q required"}), 400
    try:
        ydl_opts = { 'quiet': True, 'no_warnings': True, 'skip_download': True }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            entry = info['entries'][0] if info.get('entries') else None
            if not entry:
                return jsonify({"error": "no results"}), 404
            return jsonify({
                "status": "ok",
                "id": entry.get('id'),
                "title": entry.get('title'),
                "duration": entry.get('duration'),
                "url": f"https://youtu.be/{entry.get('id')}"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
