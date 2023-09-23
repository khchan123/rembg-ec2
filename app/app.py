import cv2
import os
import boto3
import botocore
from datetime import datetime
from rembg import remove, new_session
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask, request, send_file, make_response


BUCKET_NAME = "bucket_name_xxxxxx"
SERVER_NAME = "rembg server"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "webp"])

if UPLOAD_FOLDER not in os.listdir("."):
    os.mkdir(UPLOAD_FOLDER)


class MyFlask(Flask):
    def process_response(self, response):
        response.headers["Server"] = SERVER_NAME
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=3600; includeSubDomains; preload"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # response.headers['Access-Control-Allow-Origin'] = 'https://yoursite.com'
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        super(MyFlask, self).process_response(response)
        return response


app = MyFlask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "secret key"

s3 = boto3.client("s3")


def upload_s3(path, bucket_name, object_name):
    try:
        with open(path, "rb") as f:
            s3.upload_fileobj(f, bucket_name, object_name)
    except botocore.exceptions.ClientError as err:
        print(f"Error uploading to s3 ({err.response['Error']['Code']}): {err.response['Error']['Message']}")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def remove_background(input_path, output_path, mode=""):
    input_image = Image.open(input_path)
    if mode == "1":
        model_name = "isnet-general-use"
        session = new_session(model_name)
        output_image = remove(
            input_image,
            alpha_matting=True,
            alpha_matting_foreground_threshold=270,
            alpha_matting_background_threshold=20,
            alpha_matting_erode_size=11,
            session=session,
        )
    elif mode == "2":
        # Alpha matting is a post processing step that can be used to improve the quality of the output.
        output_image = remove(
            input_image,
            alpha_matting=True,
            alpha_matting_foreground_threshold=270,
            alpha_matting_background_threshold=20,
            alpha_matting_erode_size=11,
        )
    else:
        output_image = remove(input_image)
    output_image.save(output_path, optimize=True, quality=85)


@app.route("/rembg", methods=["POST"])
def rembg():
    try:
        mode = request.form.get("mode", "")
        file = request.files.get("file")
    except RuntimeError:
        return make_response("Bad request", 400)
    if not file or not allowed_file(file.filename):
        return make_response("Bad file", 400)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    input_filename = secure_filename(f"{timestamp}-{file.filename}")
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_filename)
    file.save(input_path)
    upload_s3(input_path, BUCKET_NAME, input_filename)
    output_filename = input_filename.split(".")[0] + ".rembg.png"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)
    remove_background(input_path, output_path, mode)
    upload_s3(output_path, BUCKET_NAME, output_filename)
    return send_file(output_path, download_name="rembg.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
