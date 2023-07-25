from flask import Flask, request, Response, jsonify, abort
from fastai.vision.all import *
from PIL import Image
import sys
import rembg
import io
import pathlib
import json
from requests_toolbelt import MultipartEncoder
from flask_cors import CORS
from getxy import get_x, get_y

from contextlib import contextmanager
@contextmanager
def set_posix_windows():
    posix_backup = pathlib.PosixPath
    try:
        pathlib.PosixPath = pathlib.WindowsPath
        yield
    finally:
        pathlib.PosixPath = posix_backup

sys.modules['__main__'].get_x = get_x
sys.modules['__main__'].get_y = get_y

app = Flask(__name__)

EXPORT_PATH = pathlib.Path("export_mk4.pkl")
with set_posix_windows():
    model = load_learner(EXPORT_PATH)
model = load_learner("export_mk4.pkl")

def random_resized_crop(img, size, scale=(0.08, 1.0), ratio=(3. / 4., 4. / 3.)):
    for attempt in range(10):
        area = img.size[0] * img.size[1]
        target_area = random.uniform(*scale) * area
        aspect_ratio = random.uniform(*ratio)

        w = int(round(math.sqrt(target_area * aspect_ratio)))
        h = int(round(math.sqrt(target_area / aspect_ratio)))

        if random.random() < 0.5:
            w, h = h, w

        if w <= img.size[0] and h <= img.size[1]:
            x1 = random.randint(0, img.size[0] - w)
            y1 = random.randint(0, img.size[1] - h)
            img = img.crop((x1, y1, x1 + w, y1 + h))
            assert(img.size == (w, h))

            return img.resize((size, size), Image.BILINEAR)

    # Fallback
    w = min(img.size[0], img.size[1])
    i = (img.size[0] - w) // 2
    j = (img.size[1] - w) // 2
    img = img.crop((i, j, i + w, j + w))
    img = img.resize((size, size), Image.BILINEAR)
    return img

# ALLOWED_ORIGINS = ["http://localhost:3000"] # Input frontend origin in [""]
# CORS(app, resources={r"/upload": {"origins": ALLOWED_ORIGINS}})

@app.route("/")
def hello():
    return "Hello"

@app.route('/remove_background', methods=['POST'])
def remove_background():
    if 'image' not in request.files:
        abort(400, description="No image provided")

    image = request.files['image'].read()
    img = Image.open(io.BytesIO(image))

    # Check if the image is JPEG
    if img.format == 'JPEG':
        # Convert it to PNG
        img = img.convert('RGB')
        with io.BytesIO() as output:
            img.save(output, format="PNG")
            image = output.getvalue()
    img = PILImage.create(image)

    # Image Classification
    img_resized = random_resized_crop(img, 128, scale=(0.7, 1.0))
    pred_class, pred_idx, outputs = model.predict(img_resized)
    cloth_class = pred_class.items[0]

    # Remove Background
    result = rembg.remove(image)

    result_img = Image.open(io.BytesIO(result))
    with io.BytesIO() as output:
        result_img.convert('RGB').save(output, format="JPEG")
        result = output.getvalue()

    # Multipart Data Create
    form_data = MultipartEncoder(
        fields={
            "image": ("result.jpeg", result, "image/jpeg"),
            "cloth_class": ("cloth_class.txt", cloth_class, "text/plain")
        }
    )
    
    headers = {"Content-Type": form_data.content_type}
    response = Response(form_data.to_string(), headers=headers)

    return response

if __name__ == '__main__':
    app.run()