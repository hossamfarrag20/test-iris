from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Npages, nprofile, Nimage
from time import sleep
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseNotFound
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from datetime import datetime, date
from django.db.models.signals import post_save
from django.dispatch import receiver
# import numpy as np
# import cv2
# import tensorflow as tf 
# from tensorflow.keras.models import load_model
# from tensorflow.keras import backend as K
import glob
import os
import subprocess
import subprocess
import time



def check_smoker_status(smoker):
    if smoker == "yes":
        return "Risky"
    elif smoker == "no":
        return "Normal"
    else:
        return "Unknown"

def check_heart_status(heart_diseases):
    if heart_diseases == "yes":
        return "Risky"
    elif heart_diseases == "no":
        return "Normal"
    else:
        return "Unknown"

@login_required(login_url='signin')
def form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        Birth_date = request.POST.get('Birth_date')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        type_order = int(request.POST.get('type_order'))
        cumulative_glucose_test = float(request.POST.get('cumulative_glucose_test'))
        heart_diseases = request.POST.get('heart_diseases').lower()
        blood_pressure = int(request.POST.get('blood_pressure'))
        cholestrol_level = int(request.POST.get('cholestrol_level'))
        smoker = request.POST.get('smoker').lower()
        Notes = request.POST.get('Notes')
        image = request.FILES.get('image')

        # Calculate the age
        birth_date = datetime.strptime(Birth_date, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        # Save the image if provided
        if image:
            tdata = Nimage(image=image)
            tdata.save()
            image_id = tdata.id
        else:
            image_id = None

        # Set cumulative statuses
        cumulative_status = ""
        cumulative_require = ""
        pressure_status = ""
        cholestrol_status = ""
        metabolic_syndrome = ""
        heart_status = check_heart_status(heart_diseases)
        smoker_status = check_smoker_status(smoker)

        if 0 < cumulative_glucose_test < 0.06:
            cumulative_status = "Normal"
        elif 0.06 <= cumulative_glucose_test <= 0.08:
            if age < 40:
                cumulative_status = "High"
                cumulative_require = "Insulin"
            else:
                cumulative_status = "High"
                cumulative_require = "Antidiabetic drugs"
        elif cumulative_glucose_test > 0.08:
            if age < 40:
                cumulative_status = "Risky"
                cumulative_require = "Insulin"
            else:
                cumulative_status = "Risky"
                cumulative_require = "Antidiabetic drugs"

        # Blood pressure check
        if 120 <= blood_pressure <= 139:
            pressure_status = "Normal"
        elif 140 <= blood_pressure <= 159:
            pressure_status = "High stage 1"
        elif 160 <= blood_pressure <= 179:
            pressure_status = "High stage 2"
        elif blood_pressure >= 180:
            pressure_status = "High stage 3"
        elif blood_pressure <= 100:
            pressure_status = "Low but no risk on eye"

        # Cholesterol level check
        if cholestrol_level < 200:
            cholestrol_status = "Normal"
        elif 200 <= cholestrol_level < 239:
            cholestrol_status = "High"
        elif cholestrol_level >= 240:
            cholestrol_status = "Risk"

        # Metabolic syndrome check
        if cumulative_glucose_test > 0.08 and blood_pressure > 140 and cholestrol_level > 240:
            metabolic_syndrome = "Metabolic syndrome"

        # Store necessary data in the session
        form_data = {
            'name': name,
            'email': email,
            'Birth_date': Birth_date,
            'phone_number': phone_number,
            'address': address,
            'type_order': type_order,
            'cumulative_glucose_test': cumulative_glucose_test,
            'heart_diseases': heart_diseases,
            'heart_status': heart_status,
            'blood_pressure': blood_pressure,
            'cholestrol_level': cholestrol_level,
            'smoker': smoker,
            'smoker_status': smoker_status,
            'Notes': Notes,
            'image_id': image_id,
            'suger_year': age,
            'cumulative_status': cumulative_status,
            'cumulative_require': cumulative_require,
            'pressure_status': pressure_status,
            'cholestrol_status': cholestrol_status,
            'metabolic_syndrome': metabolic_syndrome
        }

        if image:
            request.session['form_data'] = form_data
            return redirect('waiting_page')
        else:
            data = Npages(
                user=request.user,
                name=form_data['name'],
                email=form_data['email'],
                Birth_date=form_data['Birth_date'],
                phone_number=form_data['phone_number'],
                address=form_data['address'],
                suger_year=form_data['suger_year'],
                type_order=form_data['type_order'],
                cumulative_glucose_test=form_data['cumulative_glucose_test'],
                heart_diseases=form_data['heart_diseases'],
                blood_pressure=form_data['blood_pressure'],
                cholestrol_level=form_data['cholestrol_level'],
                smoker=form_data['smoker'],
                Notes=form_data['Notes'],
                image=None,  # No image to save
                text="",
                cumulative_status=form_data['cumulative_status'],
                cumulative_require=form_data['cumulative_require'],
                pressure_status=form_data['pressure_status'],
                cholestrol_status=form_data['cholestrol_status'],
                metabolic_syndrome=form_data['metabolic_syndrome'],
                heart_status=form_data['heart_status'],
                smoker_status=form_data['smoker_status']
            )
            data.save()
            return redirect('profile')  # Redirect to profile page

    return render(request, 'pages/form.html')

@login_required(login_url='signin')
def waiting_page(request):
    return render(request, 'eye/eye.html')

# @login_required(login_url='signin')
# def process_form(request):
#     form_data = request.session.get('form_data')
#     if not form_data:
#         return JsonResponse({'status': 'error', 'message': 'No form data found.'}, status=400)

#     request.session['processing_complete'] = False

#     if form_data['image_id']:
#         tdata = Nimage.objects.get(id=form_data['image_id'])
#         image = tdata.image

#         def crop_image_from_gray(img, tol=7):
#             if img.ndim == 2:
#                 mask = img > tol
#                 return img[np.ix_(mask.any(1), mask.any(0))]
#             elif img.ndim == 3:
#                 gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
#                 mask = gray_img > tol
#                 check_shape = img[:, :, 0][np.ix_(mask.any(1), mask.any(0))].shape[0]
#                 if check_shape == 0:
#                     return img
#                 else:
#                     img1 = img[:, :, 0][np.ix_(mask.any(1), mask.any(0))]
#                     img2 = img[:, :, 1][np.ix_(mask.any(1), mask.any(0))]
#                     img3 = img[:, :, 2][np.ix_(mask.any(1), mask.any(0))]
#                     img = np.stack([img1, img2, img3], axis=-1)
#                 return img

#         def load_color_correction(image_path, sigmaX=10):
#             img = cv2.imread(image_path)
#             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             img = crop_image_from_gray(img)
#             img = cv2.resize(img, (224, 224))
#             img = cv2.addWeighted(img, 4, cv2.GaussianBlur(img, (0, 0), sigmaX), -4, 128)
#             return img

#         def circle_crop(image_path, sigmaX=10):
#             img = cv2.imread(image_path)
#             img = crop_image_from_gray(img)
#             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#             height, width, depth = img.shape
#             x = int(width / 2)
#             y = int(height / 2)
#             r = np.amin((x, y))

#             circle_img = np.zeros((height, width), np.uint8)
#             cv2.circle(circle_img, (x, y), int(r), 1, thickness=-1)

#             img = cv2.bitwise_and(img, img, mask=circle_img)
#             img = crop_image_from_gray(img)
#             img = cv2.addWeighted(img, 4, cv2.GaussianBlur(img, (0, 0), sigmaX), -4, 128)

#             img = cv2.resize(img, (224, 224))
#             return img

#         def process_im(image_path):
#             processed_image = circle_crop(image_path)
#             processed_image_bgr = cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)
#             output_path = 'D:/my back/71_Last/Hossamf/Hossam/model/processed/processed_image.png'
#             cv2.imwrite(output_path, processed_image_bgr)
#             return output_path

#         folder_path = r'D:/my back/71_Last/Hossamf/Hossam/media/modelphoto'
#         image_path = max(glob.iglob(os.path.join(folder_path, '*.png')), key=os.path.getctime)

#         if os.path.isfile(image_path):
#             processed_image_path = process_im(image_path)

#             def preprocess_image(image_path):
#                 img = cv2.imread(image_path)
#                 img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#                 img = cv2.resize(img, (224, 224))
#                 img = img / 255.0
#                 img = np.expand_dims(img, axis=0)
#                 return img

#             def f1_score(y_true, y_pred):
#                 true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
#                 possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
#                 predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
#                 precision = true_positives / (predicted_positives + K.epsilon())
#                 recall = true_positives / (possible_positives + K.epsilon())
#                 f1_val = 2 * (precision * recall) / (precision + recall + K.epsilon())
#                 return f1_val

#             model_path = r'D:/my back/71_Last/Hossamf/Hossam/model/hossam.keras'
#             model = load_model(model_path, custom_objects={'f1_score': f1_score})

#             preprocessed_image = preprocess_image(processed_image_path)
#             predictions = model.predict(preprocessed_image)
#             class_index = np.argmax(predictions)
#             class_labels = ['class_0', 'class_1', 'class_2', 'class_3', 'class_4']
#             predicted_label = class_labels[class_index]

#             output_content = f"The predicted class is: {class_index}"
#             file_path = "D:/my back/71_Last/Hossamf/output.txt"
#             with open(file_path, 'w') as file:
#                 file.write(output_content)
#         else:
#             return JsonResponse({'status': 'error', 'message': 'No valid image found.'}, status=400)
#     else:
#         image = None
#         output_content = "No image provided."

#     data = Npages(
#         user=request.user,
#         name=form_data['name'],
#         email=form_data['email'],
#         Birth_date=form_data['Birth_date'],
#         phone_number=form_data['phone_number'],
#         address=form_data['address'],
#         suger_year=form_data['suger_year'],
#         type_order=form_data['type_order'],
#         cumulative_glucose_test=form_data['cumulative_glucose_test'],
#         heart_diseases=form_data['heart_diseases'],
#         blood_pressure=form_data['blood_pressure'],
#         cholestrol_level=form_data['cholestrol_level'],
#         smoker=form_data['smoker'],
#         Notes=form_data['Notes'],
#         image=image,
#         text=output_content,
#         cumulative_status=form_data['cumulative_status'],
#         cumulative_require=form_data['cumulative_require'],
#         pressure_status=form_data['pressure_status'],
#         cholestrol_status=form_data['cholestrol_status'],
#         metabolic_syndrome=form_data['metabolic_syndrome'],
#         heart_status=form_data['heart_status'],
#         smoker_status=form_data['smoker_status']
#     )
#     data.save()

#     request.session['processing_complete'] = True

#     return JsonResponse({'status': 'complete', 'message': 'Form processed and saved successfully.'})

# @login_required(login_url='signin')
# def check_status(request):
#     processing_complete = request.session.get('processing_complete', False)
#     if processing_complete:
#         return JsonResponse({'status': 'complete'})
#     else:
#         return JsonResponse({'status': 'incomplete'})

@login_required(login_url='signin')
def profile(request):
    user_data = Npages.objects.filter(user=request.user)
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = None
    
    return render(request, 'profile/profile.html', {'user_data': user_data, 'profile': profile, 'username': request.user.username})


@login_required(login_url='signin')
def update_profile(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = nprofile(usr=request.user)
    
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            profile.image = image
        profile.save()
        return redirect('profile')

    return render(request, 'profile/profile.html', {})
#edit and delete from Npages
@login_required(login_url='signin')
def delete(request, id):
    dale = Npages.objects.filter(user=request.user, id=id)
    dale.delete()
    return redirect('profile')

# @login_required(login_url='signin')
def edit_patient(request, id):
    patient = get_object_or_404(Npages, id=id, user=request.user)

    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.email = request.POST.get('email')
        patient.phone_number = request.POST.get('phone_number')
        patient.address = request.POST.get('address')
        patient.type_order = int(request.POST.get('type_order'))
        patient.cumulative_glucose_test = float(request.POST.get('cumulative_glucose_test'))
        patient.heart_diseases = request.POST.get('heart_diseases').lower()
        patient.blood_pressure = int(request.POST.get('blood_pressure'))
        patient.cholestrol_level = int(request.POST.get('cholestrol_level'))
        patient.smoker = request.POST.get('smoker').lower()
        patient.Notes = request.POST.get('Notes')

        birth_date = request.POST.get('Birth_date')
        if birth_date:
            try:
                parsed_birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                patient.Birth_date = parsed_birth_date

                # Calculate the age
                today = date.today()
                age = today.year - parsed_birth_date.year - ((today.month, today.day) < (parsed_birth_date.month, parsed_birth_date.day))

                # Set sugar_year to the calculated age
                patient.suger_year = age
            except ValueError:
                return render(request, 'pages/edit_patient.html', {'patient': patient, 'error': "Invalid date format"})

        # Set the status variables
        cumulative_status = ""
        cumulative_require = ""
        pressure_status = ""
        cholestrol_status = ""
        metabolic_syndrome = ""
        heart_status = check_heart_status(patient.heart_diseases)
        smoker_status = check_smoker_status(patient.smoker)

        # Cumulative glucose test check
        if 0 < patient.cumulative_glucose_test < 0.06:
            cumulative_status = "Normal"
        elif 0.06 <= patient.cumulative_glucose_test <= 0.08:
            if patient.suger_year < 40:
                cumulative_status = "High"
                cumulative_require = "Insulin"
            else:
                cumulative_status = "High"
                cumulative_require = "Antidiabetic drugs"
        elif patient.cumulative_glucose_test > 0.08:
            if patient.suger_year < 40:
                cumulative_status = "Risky"
                cumulative_require = "Insulin"
            else:
                cumulative_status = "Risky"
                cumulative_require = "Antidiabetic drugs"

        # Blood pressure check
        if 120 <= patient.blood_pressure <= 139:
            pressure_status = "Normal"
        elif 140 <= patient.blood_pressure <= 159:
            pressure_status = "High stage 1"
        elif 160 <= patient.blood_pressure <= 179:
            pressure_status = "High stage 2"
        elif patient.blood_pressure >= 180:
            pressure_status = "High stage 3"
        elif patient.blood_pressure <= 100:
            pressure_status = "Low but no risk on eye"

        # Cholesterol level check
        if patient.cholestrol_level < 200:
            cholestrol_status = "Normal"
        elif 200 <= patient.cholestrol_level < 239:
            cholestrol_status = "High"
        elif patient.cholestrol_level >= 240:
            cholestrol_status = "Risk"

        # Metabolic syndrome check
        if patient.cumulative_glucose_test > 0.08 and patient.blood_pressure > 140 and patient.cholestrol_level > 240:
            metabolic_syndrome = "Metabolic syndrome"

        # Save the status variables
        patient.cumulative_status = cumulative_status
        patient.cumulative_require = cumulative_require
        patient.pressure_status = pressure_status
        patient.cholestrol_status = cholestrol_status
        patient.metabolic_syndrome = metabolic_syndrome
        patient.heart_status = heart_status
        patient.smoker_status = smoker_status

        new_image = request.FILES.get('image')
        if new_image:
            patient.image = new_image

            # Save the new image to Nimage model
            tdata = Nimage(image=new_image)
            tdata.save()

            # Update the image id in the session
            request.session['image_id'] = tdata.id

            # Start image processing steps
            return redirect('waiting_page')
        
        # Save the patient record
        patient.save()

        return redirect('profile')

    return render(request, 'pages/edit_patient.html', {'patient': patient})





def after_edit(request):
    return render(request, 'profile/profile.html',{})


@login_required(login_url='signin')
def delete_profile(request):
    try:
        profile = request.user.profile
        profile.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('profile')


@login_required(login_url='signin')
def eye(request):
    return render(request,'eye/eye.html', {})

def waiting(request):
    return render(request,'eye/waiting.html', {})

 
@login_required(login_url='signin')
def metabolic(request):
     return render(request,'home/metabolic.html', {})