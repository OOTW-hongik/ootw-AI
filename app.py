from flask import Flask, request, Response, abort
from fastai.vision.all import *
from PIL import Image
import sys
import rembg
import io
import pathlib
from requests_toolbelt import MultipartEncoder
from flask_cors import CORS
from getxy import get_x, get_y
from random_resize import random_resized_crop
from get_clothclass import get_clothclass

sys.modules['__main__'].get_x = get_x
sys.modules['__main__'].get_y = get_y

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

logging.basicConfig(filename='app1.log', level=logging.INFO)

model = load_learner("export_mk4.pkl")

CORS(app, resources={r"/remove_background": {"origins": ["http://localhost:3000", "https://ootw.store", "https://www.ootw.store"]}})

@app.route("/")
def hello():
    return "Hello"

@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200

@app.route('/remove_background', methods=['POST'])
def remove_background():
    if 'image' not in request.files:
        abort(400, description="No image provided")

    image = request.files['image'].read()
    img = Image.open(io.BytesIO(image))

    category = request.form['category'].strip('"')

    # Check if the image is JPEG
    if img.format == 'JPEG' or img.format == 'JPG':
        # Convert it to PNG
        img = img.convert('RGB')
        with io.BytesIO() as output:
            img.save(output, format="PNG")
            image = output.getvalue()
    img = PILImage.create(image)
    
    # Image Classification
    img_resized = random_resized_crop(img, 128, scale=(0.8, 0.9))

    pred_class, pred_idx, probs = model.predict(img_resized)

    top5_idxs = probs.argsort(descending=True)[:5]
    top5_labels = [model.dls.vocab[idx] for idx in top5_idxs]

    cloth_class = get_clothclass(top5_labels, category)

    # Remove Background
    model_name = "silueta"
    session = rembg.new_session(model_name)
    result = rembg.remove(image, session=session)

    # Save result as bytes
    img = Image.open(io.BytesIO(result))
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    # Multipart Data Create
    form_data = MultipartEncoder(
        fields={
            "image": ("result.png", img_io.getvalue(), "image/png"),
            "ClothClass": ("ClothClass.txt", cloth_class, "text/plain; charset=utf-8")
        }
    )

    headers = {"Content-Type": form_data.content_type}
    response = Response(form_data.to_string(), headers=headers)

    return response

if __name__ == '__main__':
    app.run()
