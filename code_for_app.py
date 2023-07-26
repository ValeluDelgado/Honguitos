from flask import Flask, render_template, send_from_directory, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from tensorflow import keras
from keras.models import load_model
import cv2
import sys
import h5py
import os
import numpy as np
import random

from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyz'
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads/'

# Uploads settings
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Create a form class
class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, u'Image only!'),
            FileRequired(u'File was empty!')
        ]
    )
    submit = SubmitField('Upload')

# Create a router
@app.route('/', methods=['GET', 'POST'])

# def index():
def upload_image():
    form = UploadForm()
    
    if form.validate_on_submit():
        # save the file
        filename = photos.save(form.photo.data)
        file_url = url_for('static', filename='uploads/' + filename)
        model_url = os.path.realpath('./static/models/my_model.h5')
        image_url = os.path.realpath('./static/uploads/' + filename)

        model = load_model(model_url)

        image = cv2.imread(image_url)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (32, 32))     
        image = (image.astype(np.float32) / 255.0) - 0.5 
        image = np.expand_dims(image, axis=0)
        predictions = model.predict(image)
        predicted_label_index = np.argmax(predictions)
        
        # Feedback depending on the predicted label index
        feedback = ''
        
        if predicted_label_index == 0:
            feedback = 'This is an edible mushroom'
        if predicted_label_index == 1:
            feedback = 'This looks like an edible sporocarp!'
        if predicted_label_index == 2:
            feedback = "Don't eat that! Looks like a poisonous mushroom"
        if predicted_label_index == 3:
            feedback = "Careful! That looks like a poisonous sporocarp"


        # Folder Path depending on the predicted label index
        folder_path = os.path.realpath('static/model-images/' + str(predicted_label_index) + '/')
        # Here we need now an array (list) of 3 random images from the folder_path 
        file_list = os.listdir(folder_path) #this will give a list of the images of the folder
        random_images = random.sample(file_list, 3) # this will give us 3 random image files from that list 
        # That means we need a list of 3 File URLs, so we can display them in the HTML template
        random_images_urls = [url_for('static', filename='model-images/' + str(predicted_label_index) + '/' + image) for image in random_images]

        

# Function for image display: 
        #def show_random_photos(folder_path, num_photos=3):
            #image_files = [file for file in os.listdir(folder_path) if file.endswith(('.jpg', '.png', '.jpeg'))]
            #random_images = random.sample(image_files, num_photos)

            #for image_name in random_images:
                #image_path = os.path.join(folder_path, image_name)
                #img = Image.open(image_path)
                #plt.imshow(img)
                #plt.axis('off')  
                #plt.show()
    #Calling the function for the image display: 
    #folder_path = os.path.realpath('static/model-images/{predicted_label_index}') 
    #show_random_photos(folder_path, num_photos=3)

        # TEST
        # print(random_images_urls[0], file=sys.stderr)


    else:
        file_url = None
        feedback = None
        random_images_urls = None
        
    return render_template('index.html', form=form, file_url=file_url, feedback=feedback, random_images_urls=random_images_urls)

# Run the application 
if __name__ == '__main__':
    # Set debug to True for auto-reload (Not recommended for production😊)
    app.run(debug=True)