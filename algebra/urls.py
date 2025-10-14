from django.urls import path
from .views import MatrixReduceView, VectorCombinationView, VectorOperateView

urlpatterns = [
    path("matrix/reduce", MatrixReduceView.as_view(), name="matrix-reduce"),
    path("vectors/combination", VectorCombinationView.as_view(), name="vectors-combination"),
    path("vectors/operate", VectorOperateView.as_view(), name="vectors-operate"),
]
