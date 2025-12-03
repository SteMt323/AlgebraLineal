from django.urls import path
from .views import (
    MatrixReduceView, 
    MatrixOperateView,
    MatrixDeterminantView,
    VectorCombinationView, 
    VectorOperateView,
    ErrorAccumulationView,
    AbsRelErrorView,
    PropagationErrorView,
    BisectionView,
    FalsePositionView,
    NewtonRaphsonView,
    SecantView,
    DerivativeView,
    IntegralView,
)

urlpatterns = [
    path("matrix/reduce", MatrixReduceView.as_view(), name="matrix-reduce"),
    path("matrix/operate", MatrixOperateView.as_view(), name="matrix-operate"),
    path("matrix/determinant", MatrixDeterminantView.as_view(), name="matrix-determinant"),
    path("vectors/combination", VectorCombinationView.as_view(), name="vectors-combination"),
    path("vectors/operate", VectorOperateView.as_view(), name="vectors-operate"),
    path("numeric/error-accumulation", ErrorAccumulationView.as_view(), name="error-accumulation"),
    path("numeric/abs-rel-error", AbsRelErrorView.as_view(), name="abs-rel-error"),
    path("numeric/propagation-error", PropagationErrorView.as_view(), name="propagation-error"),
    path("numeric/bisection-method", BisectionView.as_view(), name="bisection-method"),
    path("numeric/false-position", FalsePositionView.as_view(), name="false-position"),
    path("numeric/newton-raphson", NewtonRaphsonView.as_view(), name="newton-raphson"),
    path("numeric/secant", SecantView.as_view(), name="secant"),
    path("calculus/derivate", DerivativeView.as_view(), name="derivate"),
    path("calculus/integral", IntegralView.as_view(), name="integral"),
]