from flask import Flask, request, send_file, render_template, after_this_request
import yt_dlp
import os
from PIL import Image
from pdf2image import convert_from_path

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/YouTube to MP3-MP4')
def youtube_to_mp34():
    return render_template('youtube_to_mp34.html')

@app.route('/jpeg_to_png')
def jpeg_to_png():
    return render_template('file_to_file.html')

@app.route('/pdf_to_jpeg')
def pdf_to_jpeg():
    return render_template('file_to_file.html')

@app.route('/jpeg_to_pdf')
def jpeg_to_pdf():
    return render_template('file_to_file.html')

@app.route('/convert_mp3', methods=['POST'])
def convert_mp3():
    url = request.form['url']
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'ffmpeg_location': 'C:/ffmpeg/bin',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        mp3_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
    
    @after_this_request
    def remove_file(response):
        try:
            os.remove(mp3_file)
        except Exception as e:
            print(f"Error deleting file: {e}")
        return response
    
    return send_file(mp3_file, as_attachment=True)

@app.route('/convert_mp4', methods=['POST'])
def convert_mp4():
    url = request.form['url']
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'ffmpeg_location': 'C:/ffmpeg/bin',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        mp4_file = ydl.prepare_filename(info_dict)
    
    @after_this_request
    def remove_file(response):
        try:
            os.remove(mp4_file)
        except Exception as e:
            print(f"Error deleting file: {e}")
        return response
    
    return send_file(mp4_file, as_attachment=True)

@app.route('/convert', methods=['POST'])
def convert():
    input_type = request.form['input_type']
    output_type = request.form['output_type']
    file = request.files['file']

    if input_type == 'jpeg' and output_type == 'png':
        img = Image.open(file)
        output_path = os.path.join('downloads', f"{os.path.splitext(file.filename)[0]}.png")
        img.save(output_path, 'PNG')
    elif input_type == 'jpeg' and output_type == 'pdf':
        img = Image.open(file)
        output_path = os.path.join('downloads', f"{os.path.splitext(file.filename)[0]}.pdf")
        img.save(output_path, 'PDF', resolution=100.0)
    elif input_type == 'pdf' and output_type == 'jpeg':
        pdf_path = os.path.join('downloads', file.filename)
        file.save(pdf_path)
        images = convert_from_path(pdf_path)
        output_path = os.path.join('downloads', f"{os.path.splitext(file.filename)[0]}.jpeg")
        images[0].save(output_path, 'JPEG')
    else:
        return "Unsupported conversion type", 400

    @after_this_request
    def remove_file(response):
        try:
            os.remove(output_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
        return response

    return send_file(output_path, as_attachment=True)
if __name__ == '__main__':
    app.run(debug=True)