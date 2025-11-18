import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

from decimal import Decimal

from .serializers import (
    MatrixReduceSerializer,
    VectorCombinationSerializer,
    VectorOperateSerializer,
    MatrixOperateSerializer,
    ErrorAccumulationSerializer,
    AbsRelErrorSerializer,
)
from .serializers import MatrixDeterminantSerializer
from .algorithms.matrix.determinants.determinant_api import determinant_api

from .algorithms.reduce.gauss_jordan import gauss_jordan_api
from .algorithms.reduce.gauss import gauss_api
from .algorithms.vectors.vectors_comb_api import linear_combination_api
from .algorithms.vectors.vectors_operations_api import vector_ops_api
from .algorithms.matrix.matrix_api import matrix_ops_api
from .algorithms.numericMethods.error_accumulation import accumulate_error_iterations
from .algorithms.numericMethods.abs_rel_error import compute_abs_rel_error

logger = logging.getLogger("algebra")
# Create your views here.

class MatrixReduceView(APIView):
    def post(self, request):
        s = MatrixReduceSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": {"code": "VALIDATION_ERROR", "messages": str(s.errors)}}, status=status.HTTP_400_BAD_REQUEST)
        payload = s.validated_data

        # Normalizar matriz aumentada
        Ab = payload.get("Ab")
        if Ab is None:
            A, b = payload["A"], payload["b"]
            Ab = [row + [b[i]] for i, row in enumerate(A)]

        method = payload["method"]
        options = payload.get("options", {})

        # Llamar a la logica de Gauss y Gauss-Jordan
        if method == "gauss":
            result = gauss_api(A=payload.get("A"), b=payload.get("b"), Ab=payload.get("Ab"), options=options)
            return Response(result, status=status.HTTP_200_OK)

        if method == "gauss-jordan":
            result = gauss_jordan_api(A=payload.get("A"), b=payload.get("b"), Ab=payload.get("Ab"), options=options)
            return Response(result, status=status.HTTP_200_OK)
    
class VectorCombinationView(APIView):
    def post(self, request):
        s = VectorCombinationSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": {"code": "VALIDATION_ERROR", "messages": str(s.errors)}}, status=status.HTTP_400_BAD_REQUEST)
        payload = s.validated_data
        try:
            result = linear_combination_api(
                A=payload["A"],
                b=payload["b"],
                options=payload.get("options")
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": {"code": "VECTOR_COMB_ERROR", "message": str(e)}}, status=status.HTTP_400_BAD_REQUEST)
    
class VectorOperateView(APIView):
    def post(self, request):
        s = VectorOperateSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": {"code": "VALIDATION_ERROR", "message": str(s.errors)}},
                            status=status.HTTP_400_BAD_REQUEST)
        payload = s.validated_data
        try:
            result = vector_ops_api(
                operation=payload["operation"],
                vectors=payload["vectors"],
                scalars=payload.get("scalars"),
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": {"code": "VECTOR_OP_ERROR", "message": str(e)}}, status=status.HTTP_400_BAD_REQUEST)


class MatrixOperateView(APIView):
    def post(self, request):
        s = MatrixOperateSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": {"code": "VALIDATION_ERROR", "message": str(s.errors)}}, status=status.HTTP_400_BAD_REQUEST)
        payload = s.validated_data
        try:
            result = matrix_ops_api(
                operation=payload["operation"],
                A=payload.get("A"),
                B=payload.get("B"),
                matrices=payload.get("matrices"),
                scalar=payload.get("scalar"),
                options=payload.get("options"),
            )
            # If wrapper returned an error dict, forward as 400
            if isinstance(result, dict) and result.get('error'):
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": {"code": "MATRIX_OP_ERROR", "message": str(e)}}, status=status.HTTP_400_BAD_REQUEST)

class MatrixDeterminantView(APIView):
    def post(self, request):
        s = MatrixDeterminantSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": {"code": "VALIDATION_ERROR", "message": str(s.errors)}}, status=status.HTTP_400_BAD_REQUEST)
        payload = s.validated_data
        try:
            res = determinant_api(A=payload["A"], method=payload.get("method"), options=payload.get("options"))
            # determinant_api returns dict or raises
            if isinstance(res, dict) and res.get('error'):
                return Response(res, status=status.HTTP_400_BAD_REQUEST)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": {"code": "DETERMINANT_ERROR", "message": str(e)}}, status=status.HTTP_400_BAD_REQUEST)
        

## VISTAS DE MÉTODOS NUMÉRICOS ##

class ErrorAccumulationView(APIView):
    def post(self, request):
        s = ErrorAccumulationSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": "VALIDATION_ERROR", "details": s.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = s.validated_data
        initial_amount: Decimal = data['initial_amount']
        iterations: int = data['iterations']
        mode: str = data['mode']
        rate: Decimal = data.get('rate', Decimal("0.0625"))
        approx_decimals: int = data.get('approx_decimals', 2)
        interest_display_decimals: int = data.get('interest_display_decimals', 4)

        try:
            result = accumulate_error_iterations(
                initial_amount=initial_amount,
                iterations=iterations,
                mode=mode,
                rate=rate,
                approx_decimals=approx_decimals,
                interest_display_decimals=interest_display_decimals
            )
            # Convertir Decimals en str para JSON seguro (o deja números; DRF convertirá Decimals a strings por defecto)
            # Aquí devolvemos los Decimals tal cual; DRF serializa Decimal a string en JSON.
            return Response({"input": {"initial_amount": str(initial_amount), "iterations": iterations, "mode": mode, "rate": str(rate)}, "data": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "COMPUTATION_ERROR", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AbsRelErrorView(APIView):
    def post(self, request):
        s = AbsRelErrorSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": "VALIDATION_ERROR", "details": s.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = s.validated_data
        true_value: Decimal = data['true_value']
        approx_value: Decimal = data['approx_value']
        decimals_display: int = data.get('decimals_display', 6)

        try:
            res = compute_abs_rel_error(true_value=true_value, approx_value=approx_value, decimals_display=decimals_display)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "COMPUTATION_ERROR", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)