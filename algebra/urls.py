from django.urls import path
from .views import (
    MatrixReduceView, 
    MatrixOperateView,
    MatrixDeterminantView,
    VectorCombinationView, 
    VectorOperateView,
    ErrorAccumulationView,
    AbsRelErrorView,
)

urlpatterns = [
    path("matrix/reduce", MatrixReduceView.as_view(), name="matrix-reduce"),
    path("matrix/operate", MatrixOperateView.as_view(), name="matrix-operate"),
    path("matrix/determinant", MatrixDeterminantView.as_view(), name="matrix-determinant"),
    path("vectors/combination", VectorCombinationView.as_view(), name="vectors-combination"),
    path("vectors/operate", VectorOperateView.as_view(), name="vectors-operate"),
    path("numeric/error-accumulation", ErrorAccumulationView.as_view(), name="error-accumulation"),
    path("numeric/abs-rel-error", AbsRelErrorView.as_view(), name="abs-rel-error"),
]
