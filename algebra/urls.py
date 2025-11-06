from django.urls import path
from .views import MatrixReduceView, VectorCombinationView, VectorOperateView
from .views import MatrixOperateView

urlpatterns = [
    path("matrix/reduce", MatrixReduceView.as_view(), name="matrix-reduce"),
    path("vectors/combination", VectorCombinationView.as_view(), name="vectors-combination"),
    path("vectors/operate", VectorOperateView.as_view(), name="vectors-operate"),
    path("matrix/operate", MatrixOperateView.as_view(), name="matrix-operate"),
]
