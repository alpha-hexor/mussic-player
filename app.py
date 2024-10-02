from flask import Flask, render_template, request, jsonify
from music import Music
import re

app = Flask(__name__)
music_client = Music()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    result = music_client.search_music(query)
    return jsonify(result)

@app.route('/get_audio_url', methods=['POST'])
def get_audio_url():
    video_id = request.json['video_id']
    audio_url = music_client.get_audio_url(video_id)
    return jsonify({'audio_url': audio_url})

@app.route('/get_lyrics', methods=['POST'])
def get_lyrics():
    video_id = request.json['video_id']
    lyrics = music_client.get_lyrics(video_id)
    if lyrics:
        lyrics = re.sub(r'\\r','',lyrics)
        lyrics = re.sub(r'\\n','<br>',lyrics)
    return jsonify({'lyrics': lyrics})

@app.route('/next_songs', methods=['POST'])
def next_songs():
    video_id = request.json['video_id']
    next_songs = music_client.next_song(video_id)
    return jsonify({'next_songs': next_songs})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)