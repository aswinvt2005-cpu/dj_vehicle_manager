"""
URL configuration for VehicleManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from vehicle.views import VehicleManager, VehicleDetails,CustomerManager,RentalManager,ReturnVehicle

urlpatterns = [
    path('admin/', admin.site.urls),
    path('vehicles/', VehicleManager.as_view()),
    path('vehicles/<int:id>/', VehicleDetails.as_view()),
    path('customers/', CustomerManager.as_view()),
    path('rentals/', RentalManager.as_view()),
    path('returns/', ReturnVehicle.as_view()),

]
