from django.contrib import admin
from django.urls import path
from layout import views as layout_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('raw-image/layout/<int:pk>', layout_views.RawImageLayoutDetailView.as_view(), name='rawimage-layout')
]
