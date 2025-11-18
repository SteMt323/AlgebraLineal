from django.urls import path
from .views import MatrixReduceView, VectorCombinationView, VectorOperateView
from .views import MatrixOperateView
from .views import MatrixDeterminantView
from .views import ErrorAccumulationView

urlpatterns = [
    path("matrix/reduce", MatrixReduceView.as_view(), name="matrix-reduce"),
    path("matrix/operate", MatrixOperateView.as_view(), name="matrix-operate"),
    path("matrix/determinant", MatrixDeterminantView.as_view(), name="matrix-determinant"),
    path("vectors/combination", VectorCombinationView.as_view(), name="vectors-combination"),
    path("vectors/operate", VectorOperateView.as_view(), name="vectors-operate"),
    path("numeric/error-accumulation", ErrorAccumulationView.as_view(), name="error-accumulation"),
]
