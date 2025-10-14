import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

from .serializers import (
    MatrixReduceSerializer,
    VectorCombinationSerializer,
    VectorOperateSerializer
)

from .algorithms.reduce.gauss_jordan import gauss_jordan_api
from .algorithms.reduce.gauss import gauss_api
from .algorithms.vectors.vectors_comb import linear_combination_api
from .algorithms.vectors.vectors_operations import vector_ops_api

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