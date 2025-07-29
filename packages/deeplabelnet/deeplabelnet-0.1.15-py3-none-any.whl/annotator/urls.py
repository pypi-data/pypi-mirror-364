from django.urls import path
from . import views

urlpatterns = [

    # Main pages
    path('check-media/', views.check_media_access, name='check_media'),
    path('media-diagnostic/', views.media_diagnostic, name='media_diagnostic'),
    path('', views.home, name='home'),
    path('manual-annotation/', views.manual_annotation, name='manual_annotation'),
    path('train-model/', views.train_model, name='train_model'),
    path('auto-annotation/', views.auto_annotation, name='auto_annotation'),
    # path('yolo-detect/', views.yolo_detect, name='yolo_detect'),
    # API endpoints
    path('api/select-folder/', views.select_folder, name='select_folder'),
    path('api/save-annotations/', views.save_annotations, name='save_annotations'),
    path('api/load-annotations/', views.load_annotations, name='load_annotations'),
    path('api/start-training/', views.start_training, name='start_training'),
    path('api/check-training-status/<str:job_id>/', views.check_training_status, name='check_training_status'),
    path('api/run-auto-annotation/', views.run_auto_annotation, name='run_auto_annotation'),
    path('api/export-annotations/<str:format_type>/', views.export_annotations, name='export_annotations'),
    path('api/download-model/<str:model_id>/', views.download_model, name='download_model'),


]