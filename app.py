from flask import Flask, request, jsonify
import whisper
import os
import uuid

app = Flask(__name__)
model = whisper.load_model("small")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    "mp3", "wav", "m4a", "ogg", "flac", "aac", "wma", "webm", "mp4", "mpeg"
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    filepath = None

    try:
        if "audio" not in request.files:
            return jsonify({
                "status": False,
                "message": "No audio file provided (field name must be 'audio')"
            }), 400

        file = request.files["audio"]

        if file.filename == "":
            return jsonify({
                "status": False,
                "message": "Empty filename"
            }), 400

        if not allowed_file(file.filename):
            return jsonify({
                "status": False,
                "message": "Unsupported file type"
            }), 400

        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)
        os.system(f"ffmpeg -i {filepath} {filepath}.wav")
        result = model.transcribe(f"{filepath}.wav", language="ar", fp16=False)

        return jsonify({
            "status": True,
            "text": result["text"]
        })

    except Exception as e:
        return jsonify({
            "status": False,
            "message": str(e)
        }), 500

    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
