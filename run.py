import requests
import base64

image_path = 'cloth3.jpeg'

with open(image_path, 'rb') as file:
    files = {'image': file}
    response = requests.post('http://127.0.0.1:5000/remove_background', files=files)

if response.ok:
    data = response.json()
    print('Class:', data['class'])

    img_data = base64.b64decode(data['image'])
    with open('result3.jpeg', 'wb') as output_file:
        output_file.write(img_data)
else:
    print('Error')