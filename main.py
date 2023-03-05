import os
import uuid
import flask
import urllib
from PIL import Image
from keras.models import load_model
from flask import Flask, render_template, request, send_file
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.utils import load_img

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, 'keras_model.h5'))

ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


classes = ['Nothing', 'Battery', 'Cardboard', 'Cans', 'Paper', 'Shoes', 'Glass', 'Plastic']


def predict(filename, model):
    img = load_img(filename, target_size=(224, 224))
    img = img_to_array(img)
    img = img.reshape(1, 224, 224, 3)

    img = img.astype('float32')
    img = img / 255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(8):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i] * 100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/success', methods=['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')
    if request.method == 'POST':
        if (request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename + ".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)
                category_result = ""
                if(class_result[0] == 'Battery'):
                   category_result = "Hazardous"
                if (class_result[0] == 'Cardboard'):
                    category_result = "Recycable"
                if (class_result[0] == 'Cans'):
                    category_result = "Recycable"
                if (class_result[0] == 'Paper'):
                    category_result = "Recycable"
                if (class_result[0] == 'Shoes'):
                    category_result = "Residual"
                if (class_result[0] == 'Glass'):
                    category_result = "Recycable"
                if (class_result[0] == 'Plastic'):
                    category_result = "Non-biodegradable"

                predictions = {
                    "class1": class_result[0],
                    "prob1": prob_result[0],
                    "category": category_result,
                }

            except Exception as e:
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)


        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)
                category_result=""
                if (class_result[0] == 'Battery'):
                    category_result = "Hazardous"
                if (class_result[0] == 'Cardboard'):
                    category_result = "Recycable"
                if (class_result[0] == 'Cans'):
                    category_result = "Recycable"
                if (class_result[0] == 'Paper'):
                    category_result = "Recycable"
                if (class_result[0] == 'Shoes'):
                    category_result = "Residual"
                if (class_result[0] == 'Glass'):
                    category_result = "Recycable"
                if (class_result[0] == 'Plastic'):
                    category_result = "Non-biodegradable"

                predictions = {
                    "class1": class_result[0],
                    "prob1": prob_result[0],
                    "category": category_result,
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)


