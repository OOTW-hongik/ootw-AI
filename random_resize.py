from fastai.vision.all import *

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
