from flask import Flask, request, Response, jsonify, abort
from fastai.vision.all import *
from PIL import Image
import rembg
import io
import pathlib
import json
import multipart
from flask_cors import CORS

# from contextlib import contextmanager
# @contextmanager
# def set_posix_windows():
#     posix_backup = pathlib.PosixPath
#     try:
#         pathlib.PosixPath = pathlib.WindowsPath
#         yield
#     finally:
#         pathlib.PosixPath = posix_backup

# EXPORT_PATH = pathlib.Path("export_mk4.pkl")
# with set_posix_windows():
#     model = load_learner(EXPORT_PATH)

app = Flask(__name__)

def get_x(r):
    return r
def get_y(r):
    return r

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

@app.route('/remove_background', methods=['POST'])
def remove_background():
    if 'image' not in request.files:
        abort(400, description="No image provided")

    image = request.files['image'].read()
    img = PILImage.create(image)

    # Image Classification
    img_resized = random_resized_crop(img, 128, scale=(0.7, 1.0))
    pred_class, pred_idx, outputs = model.predict(img_resized)
    cloth_class = {'cloth_class' : pred_class}

    # Remove Background
    result = rembg.remove(image)

    # Save result as bytes
    img = Image.open(io.BytesIO(result))
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)

    # Multipart Data Create
    form_data = multipart.Multipart()
    form_data.field("image", img_io.getvalue(), "result.jpeg", "image/jpeg")   
    form_data.field("cloth_class", json.dumps(cloth_class), "cloth_class.json", "application/json")
    
    headers = {"Content-Type": f"multipart/form-data; boundary={form_data.boundary}"}
    response = Response(form_data, headers=headers)

    return response

if __name__ == '__main__':
    app.run()