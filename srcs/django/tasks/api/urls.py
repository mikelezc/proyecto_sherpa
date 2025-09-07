from django.urls import path
from rest_framework.routers import DefaultRouter

# Para cuando agregues viewsets en el futuro
router = DefaultRouter()

urlpatterns = [
    # API endpoints van aquí
    # Ejemplo: path('create/', CreateTaskView.as_view(), name='create_task'),
]

# Añadir las rutas del router
urlpatterns += router.urls
