from django.urls import path
from . import views

app_name = 'batch'  # Setting the app namespace

urlpatterns = [
    path('', views.batch_list, name='batch_list'),
    path('create/', views.create_batch, name='create_batch'),
    path('<int:batch_id>/edit/', views.edit_batch, name='edit_batch'),
    path('<int:batch_id>/', views.batch_detail, name='batch_detail'),
    path('<int:batch_id>/assign/<int:enquiry_id>/', views.assign_to_batch, name='assign_to_batch'),
    path('<int:batch_id>/remove/<int:enquiry_id>/', views.remove_from_batch, name='remove_from_batch'),
    path('<int:batch_id>/bulk_assign/', views.bulk_assign_to_batch, name='bulk_assign_to_batch'),
    path('<int:batch_id>/bulk_remove/', views.bulk_remove_from_batch, name='bulk_remove_from_batch'),
]