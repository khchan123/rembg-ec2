import cv2
import os
from rembg import remove, new_session
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask,request,render_template

SERVER_NAME = "rembg server"
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','webp'])

if 'static' not in os.listdir('.'):
    os.mkdir('static')

if 'uploads' not in os.listdir('static/'):
    os.mkdir('static/uploads')

class MyFlask(Flask):
    def process_response(self, response):
        response.headers['Server'] = SERVER_NAME
        response.headers['Strict-Transport-Security'] = 'max-age=3600; includeSubDomains; preload'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # response.headers['Access-Control-Allow-Origin'] = 'https://yoursite.com'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Resource-Policy'] = 'same-site'
        super(MyFlask, self).process_response(response)
        return(response)

app = MyFlask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def remove_background(input_path, output_path):
    input = Image.open(input_path)
    model_name = "isnet-general-use"
    session = new_session(model_name)
    # Alpha metting is a post processing step that can be used to improve the quality of the output.
    # output = remove(input, alpha_matting=True, alpha_matting_foreground_threshold=270,alpha_matting_background_threshold=20, alpha_matting_erode_size=11)
    # You can use the post_process_mask argument to post process the mask to get better results.
    output = remove(input, post_process_mask=True, session=session)
    # output = remove(input)
    output.save(output_path)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/remback', methods=['POST'])
def remback():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        rembg_img_name = filename.split('.')[0]+"_rembg.png"
        remove_background(UPLOAD_FOLDER+'/'+filename,UPLOAD_FOLDER+'/'+rembg_img_name)
        return render_template('home.html', org_img_name=filename, rembg_img_name=rembg_img_name)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)