from flask import Flask, request, send_file
import os
import time
import yt_dlp
import re
import subprocess
import threading

app = Flask(__name__)

def convert_to_mobile_url(url):
    if not url:
        return url
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if video_id_match:
        video_id = video_id_match.group(1)
        return f"https://m.youtube.com/watch?v={video_id}"
    return url

@app.route('/download', methods=['GET'])
def download_file():
    raw_url = request.args.get('url')
    file_type = request.args.get('type', 'video')

    if not raw_url:
        return "URL is missing", 400

    video_url = convert_to_mobile_url(raw_url)
    timestamp = int(time.time())
    cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

    if file_type == 'audio':
        file_name = f"audio_{timestamp}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '5',
            }],
            'outtmpl': f"audio_{timestamp}.%(ext)s",
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
        mimetype = 'audio/mpeg'
    else:
        file_name = f"video_{timestamp}.mp4"
        ydl_opts = {
            'format': '22/18/b[height<=480]',
            'outtmpl': file_name,
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['android,web']}}
        }
        mimetype = 'video/mp4'

    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        actual_file = file_name
        if file_type == 'audio':
            actual_file = f"audio_{timestamp}.mp3"
            if not os.path.exists(actual_file):
                for f in os.listdir('.'):
                    if f.startswith(f"audio_{timestamp}") and f.endswith('.mp3'):
                        actual_file = f
                        break

        if not os.path.exists(actual_file):
            return "Download failed: File not found", 500

        return send_file(actual_file, as_attachment=True, mimetype=mimetype)

    except Exception as e:
        print(f"[ERROR]: {e}")
        return str(e), 500
        
    finally:
        time.sleep(2)
        for f in [file_name, f"audio_{timestamp}.mp3", f"video_{timestamp}.mp4"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

def start_tunnel():
    time.sleep(3)
    try:
        cmd = ["ssh", "-p", "443", "-o", "StrictHostKeyChecking=no", "-R0:localhost:5000", "a.pinggy.io"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        print("\n==================================================")
        print("🚀 تم تفعيل نفق Pinggy بنجاح!")
        print("==================================================")

        for line in process.stdout:
            if "run.pinggy-free.link" in line or "free.pinggy.net" in line:
                parts = line.strip().split()
                for part in parts:
                    if part.startswith("https://"):
                        print(f"\n🔗 الرابط المباشر للاتصال: \n👉 {part}\n")
                        break
            
    except Exception as e:
        print(f"[TUNNEL ERROR]: {e}")

if __name__ == '__main__':
    tunnel_thread = threading.Thread(target=start_tunnel)
    tunnel_thread.daemon = True
    tunnel_thread.start()

    print("🌐 جاري تشغيل سيرفر Flask المحلي...")
    app.run(host='0.0.0.0', port=5000)
