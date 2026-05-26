from flask import Flask, request, jsonify
import whisper
import os
import uuid
# استيراد وحدة ffmpeg من imageio
import imageio.plugins.ffmpeg as ffmpeg_plugin

app = Flask(__name__)

# --- تحميل ffmpeg (يتم مرة واحدة عند بدء التشغيل) ---
print("Checking/Downloading ffmpeg...")
try:
    # يقوم imageio بتنزيل ffmpeg تلقائياً إذا لم يجده
    ffmpeg_plugin.download()
    # الحصول على المسار الكامل لملف ffmpeg التنفيذي
    FFMPEG_PATH = ffmpeg_plugin.get_exe()
    print(f"ffmpeg is ready at: {FFMPEG_PATH}")
except Exception as e:
    print(f"ERROR loading ffmpeg: {e}")
    FFMPEG_PATH = 'ffmpeg' # Fallback for local testing

# --- تحميل نموذج Whisper (يتم مرة واحدة) ---
print("Loading Whisper model...")
# استخدام الكاش للتحميل مرة واحدة فقط
model = whisper.load_model("small")
print("Whisper model loaded.")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "flac", "aac", "wma", "webm", "mp4", "mpeg"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    # المنطق الرئيسي للـ API يبقى كما هو، لكن مع استخدام FFMPEG_PATH
    filepath = None
    wav_path = None
    try:
        if "audio" not in request.files:
            return jsonify({"status": False, "message": "No audio file provided (field name must be 'audio')"}), 400

        file = request.files["audio"]
        if file.filename == "":
            return jsonify({"status": False, "message": "Empty filename"}), 400
        if not allowed_file(file.filename):
            return jsonify({"status": False, "message": "Unsupported file type"}), 400

        # حفظ الملف المرفوع
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # --- استخدام ffmpeg من imageio للتحويل ---
        wav_path = os.path.splitext(filepath)[0] + ".wav"
        # استخدام FFMPEG_PATH الذي تم إعداده عالمياً
        command = f"{FFMPEG_PATH} -i {filepath} {wav_path} -y"
        os.system(command)

        # نسخ الصوت باستخدام Whisper
        result = model.transcribe(wav_path, language="ar", fp16=False)

        return jsonify({"status": True, "text": result["text"]})

    except Exception as e:
        # تسجيل الخطأ لمساعدتك في التصحيح
        app.logger.error(f"Error in transcribe_audio: {str(e)}")
        return jsonify({"status": False, "message": str(e)}), 500
    finally:
        # تنظيف الملفات المؤقتة
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == "__main__":
    # المنفذ 8000 يتناسب مع إعداد gunicorn
    app.run(host="0.0.0.0", port=8000)
