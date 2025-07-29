import os
import json
import shutil
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
# from ultralytics import YOLO



# Define the media directory where uploaded images will be stored
MEDIA_DIR = os.path.join(settings.MEDIA_ROOT, 'images')
os.makedirs(MEDIA_DIR, exist_ok=True)




def home(request):
    """
    Render the home page of the annotation tool.
    """
    return render(request, 'annotator/home.html')


def manual_annotation(request):
    """
    Render the manual annotation interface with the uploaded images.
    """
    # Get list of image files in the media directory
    image_files = []

    if os.path.exists(MEDIA_DIR):
        for file in os.listdir(MEDIA_DIR):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(file)

    context = {
        'image_files': image_files,
        'media_url': settings.MEDIA_URL,
    }
    return render(request, 'annotator/interface.html', context)


#to check media access and media diagnostic
def check_media_access(request):
    from django.http import JsonResponse
    import os

    media_dir = settings.MEDIA_ROOT
    media_exists = os.path.exists(media_dir)
    files_count = 0

    if media_exists:
        files = [f for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))]
        files_count = len(files)

    return JsonResponse({
        'media_dir_exists': media_exists,
        'media_dir_path': media_dir,
        'files_count': files_count
    })


def media_diagnostic(request):
    import os
    from django.http import HttpResponse
    from django.conf import settings

    output = []
    output.append(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    output.append(f"MEDIA_URL: {settings.MEDIA_URL}")
    output.append(f"Directory exists: {os.path.exists(settings.MEDIA_ROOT)}")

    if os.path.exists(settings.MEDIA_ROOT):
        files = os.listdir(settings.MEDIA_ROOT)
        output.append(f"Files in directory ({len(files)}):")
        for file in files:
            file_path = os.path.join(settings.MEDIA_ROOT, file)
            size = os.path.getsize(file_path) if os.path.isfile(file_path) else "N/A"
            output.append(f"  - {file} (Size: {size} bytes)")

    return HttpResponse("<br>".join(output), content_type="text/html")


def train_model(request):
    """
    Render the training interface with the uploaded images.
    """
    # Get list of image files in the media directory
    image_files = []
    if os.path.exists(MEDIA_DIR):
        for file in os.listdir(MEDIA_DIR):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(file)

    context = {
        'image_files': image_files,
        'media_url': settings.MEDIA_URL,
    }
    return render(request, 'annotator/train.html', context)


def auto_annotation(request):
    """
    Render the auto annotation interface with the uploaded images.
    """
    # Get list of image files in the media directory
    image_files = []
    if os.path.exists(MEDIA_DIR):
        for file in os.listdir(MEDIA_DIR):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(file)

    context = {
        'image_files': image_files,
        'media_url': settings.MEDIA_URL,
    }
    return render(request, 'annotator/auto.html', context)


@csrf_exempt
def select_folder(request):
    """
    Handle the upload of multiple image files (folder upload).
    """
    if request.method == 'POST' and request.FILES:
        # Clear existing images if requested
        if request.POST.get('clear_existing', False):
            if os.path.exists(MEDIA_DIR):
                shutil.rmtree(MEDIA_DIR)
                os.makedirs(MEDIA_DIR, exist_ok=True)

        # Get all files from the request
        files = request.FILES.getlist('folder')

        # Save each file to the media directory
        fs = FileSystemStorage(location=MEDIA_DIR)
        saved_files = []

        for file in files:
            # Only save image files
            if file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                filename = fs.save(file.name, file)
                saved_files.append(filename)

        # Determine which page to redirect to based on the request
        referer = request.META.get('HTTP_REFERER', '')
        if 'train' in referer:
            return redirect('train_model')
        elif 'auto' in referer:
            return redirect('auto_annotation')
        else:
            return redirect('manual_annotation')
    else:
        return redirect('home')


@csrf_exempt
def save_annotations(request):
    """
    Save annotations to a JSON file on the server.
    """
    if request.method == 'POST':
        try:
            # Get annotations data from request
            data = json.loads(request.body)
            annotations = data.get('annotations', {})

            # Save annotations to a file
            annotations_dir = os.path.join(settings.MEDIA_ROOT, 'annotations')
            os.makedirs(annotations_dir, exist_ok=True)

            file_path = os.path.join(annotations_dir, 'annotations.json')
            with open(file_path, 'w') as f:
                json.dump(annotations, f, indent=2)

            return JsonResponse({'status': 'success', 'message': 'Annotations saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def load_annotations(request):
    """
    Load annotations from a JSON file on the server.
    """
    if request.method == 'GET':
        try:
            # Check if annotations file exists
            annotations_dir = os.path.join(settings.MEDIA_ROOT, 'annotations')
            file_path = os.path.join(annotations_dir, 'annotations.json')

            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    annotations = json.load(f)
                return JsonResponse({'status': 'success', 'annotations': annotations})
            else:
                return JsonResponse({'status': 'success', 'annotations': {}})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def start_training(request):
    """
    Handle model training request.
    This is a placeholder that would integrate with actual model training code.
    """
    if request.method == 'POST':
        try:
            # Get training parameters from request
            data = json.loads(request.body)
            model_type = data.get('model', 'faster_rcnn')
            annotations = data.get('annotations', {})

            # In a real implementation, this would start a background task for model training
            # For now, we'll just simulate success

            return JsonResponse({
                'status': 'success',
                'message': f'Training started for model {model_type}',
                'job_id': '12345'  # Would be a real job ID in actual implementation
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def check_training_status(request, job_id):
    """
    Check the status of a training job.
    This is a placeholder that would integrate with actual model training status checks.
    """
    if request.method == 'GET':
        # In a real implementation, this would check the status of the training job
        # For now, we'll just return a simulated status

        return JsonResponse({
            'status': 'success',
            'training_status': 'in_progress',
            'progress': 75,  # Percentage complete
            'message': 'Training in progress'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def run_auto_annotation(request):
    """
    Run automatic annotation on an image using a selected model.
    This is a placeholder that would integrate with actual model inference code.
    """
    if request.method == 'POST':
        try:
            # Get auto annotation parameters from request
            data = json.loads(request.body)
            model_type = data.get('model', 'fasterrcnn')
            image_path = data.get('image', '')
            confidence = data.get('confidence', 0.5)

            # In a real implementation, this would run model inference on the image
            # For now, we'll just return simulated annotations

            # Simulated annotations (would be real model output in actual implementation)
            simulated_annotations = [
                {
                    'type': 'bbox',
                    'x': 100,
                    'y': 100,
                    'width': 200,
                    'height': 150,
                    'label': 'person',
                    'confidence': 0.85
                },
                {
                    'type': 'bbox',
                    'x': 400,
                    'y': 200,
                    'width': 100,
                    'height': 100,
                    'label': 'dog',
                    'confidence': 0.72
                }
            ]

            return JsonResponse({
                'status': 'success',
                'annotations': simulated_annotations,
                'message': f'Auto annotation completed with {model_type}'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def export_annotations(request, format_type):
    """
    Export annotations in various formats (JSON, Pascal VOC, COCO, etc.)
    """
    if request.method == 'POST':
        try:
            # Get annotations data from request
            data = json.loads(request.body)
            annotations = data.get('annotations', {})

            if format_type == 'json':
                # Return annotations as JSON download
                response = HttpResponse(
                    json.dumps(annotations, indent=2),
                    content_type='application/json'
                )
                response['Content-Disposition'] = 'attachment; filename="annotations.json"'
                return response

            elif format_type == 'pascal_voc':
                # In a real implementation, this would convert annotations to Pascal VOC format
                # For now, just return a placeholder message
                return JsonResponse({
                    'status': 'error',
                    'message': 'Pascal VOC export not implemented yet'
                })

            elif format_type == 'coco':
                # In a real implementation, this would convert annotations to COCO format
                # For now, just return a placeholder message
                return JsonResponse({
                    'status': 'error',
                    'message': 'COCO export not implemented yet'
                })

            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Unsupported export format: {format_type}'
                }, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def download_model(request, model_id):
    """
    Download a trained model.
    This is a placeholder that would integrate with actual model storage.
    """
    # In a real implementation, this would retrieve the model file and send it as a download
    # For now, just return a placeholder message
    return HttpResponse("Model download functionality not implemented yet")

def run_yolo_detection(
    model_path="D:/aro_yolomdl/yolov10/runs/detect/train2/weights/best.pt",
    image_source="D:/out_of_proj_aro_work/aro_test_imgs",
    conf_threshold=0.25,
    save_txt=True,
    save_img=True
):
    # Load the model
    model = YOLO(model_path)

    # Run prediction
    results = model.predict(
        source=image_source,
        conf=conf_threshold,
        save=save_img,
        save_txt=save_txt
    )

#
# def detect_objects(model_path, source_path, conf_threshold=0.5, save=True, save_txt=True, save_dir=None):
#     model = YOLO(model_path)
#
#     if save_dir and not os.path.exists(save_dir):
#         os.makedirs(save_dir)
#
#     results = model.predict(
#         source=source_path,
#         conf=conf_threshold,
#         save=save,
#         save_txt=save_txt,
#         save_dir=save_dir
#     )
#     return results
#
#
# def yolo_detect(request):
#     if request.method == "POST" and request.FILES.get('model') and request.FILES.get('images'):
#         model_file = request.FILES['model']
#         image_files = request.FILES.getlist('images')
#         save_dir = request.POST.get('save_dir')
#
#         fs = FileSystemStorage(location=settings.MEDIA_ROOT)
#         model_path = fs.save(model_file.name, model_file)
#
#         images_dir = os.path.join(settings.MEDIA_ROOT, 'images')
#         os.makedirs(images_dir, exist_ok=True)
#
#         image_paths = []
#         for image in image_files:
#             image_path = os.path.join(images_dir, image.name)
#             fs.save(image_path, image)
#             image_paths.append(image_path)
#
#         results_dir = os.path.join(settings.MEDIA_ROOT, save_dir)
#         os.makedirs(results_dir, exist_ok=True)
#
#         results = []
#         for image_path in image_paths:
#             result = detect_objects(
#                 model_path=model_path,
#                 source_path=image_path,
#                 save=True,
#                 save_txt=True,
#                 save_dir=results_dir
#             )
#             results.append({
#                 "image": image_path,
#                 "output_files": os.listdir(results_dir)
#             })
#
#         return JsonResponse({
#             "message": "Detection complete",
#             "results": results
#         })
#
#     return render(request, "yolo_form.html")


