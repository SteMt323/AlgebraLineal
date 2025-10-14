from rest_framework import serializers

class MatrixReduceSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=['gauss', 'gauss-jordan'])
    A = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()), required=False)
    b = serializers.ListField(child=serializers.FloatField(), required=False)
    Ab = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()), required=False)
    options = serializers.DictField(required=False)

    def validate(self, data):
        A, b, Ab = data.get('A'), data.get('b'), data.get('Ab')

        if Ab is None and A is None:
            raise serializers.ValidationError("Debes enviar 'Ab' o 'A'.")
        if Ab is not None and A is not None:
            raise serializers.ValidationError("Envía solo 'Ab' o 'A', no ambos.")
        if A is not None and b is None:
            raise serializers.ValidationError("Si envías 'A', también debes enviar 'b'.")
        if A is not None and b is not None:
            rows = len(A)
            if rows == 0:
                raise serializers.ValidationError("A no puede ser vacía.")
            if any(len(row) != len(A[0]) for row in A):
                raise serializers.ValidationError("Todas las filas de A deben tener la misma longitud.")
            if len(b) != rows:
                raise serializers.ValidationError(f"Dimensiones inconsistentes: A es {rows}x{len(A[0])} y b tiene longitud {len(b)}.")
        if Ab is not None:
            if len(Ab) == 0 or len(Ab[0]) < 2:
                raise serializers.ValidationError("La matriz aumentada debe tener al menos 2 columnas.")
            if any(len(row) != len(Ab[0]) for row in Ab):
                raise serializers.ValidationError("Todas las filas de Ab deben tener la misma longitud.")
        return data
    
class VectorCombinationSerializer(serializers.Serializer):
    A = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()))
    b = serializers.ListField(child=serializers.FloatField())
    options = serializers.DictField(required=False)

    def validate(self, data):
        A, b = data.get('A'), data.get('b')

        if not A:
            raise serializers.ValidationError("A no puede ser vacía.")

        # todas las filas del mismo largo
        n = len(A[0])
        if any(len(row) != n for row in A):
            raise serializers.ValidationError("Todas las filas de A deben tener la misma longitud.")

        m = len(A)
        if len(b) != m:
            raise serializers.ValidationError(
                f"Dimensiones inconsistentes: A es {m}x{n} y b tiene longitud {len(b)} (debe ser {m})."
            )
        return data



    
class VectorOperateSerializer(serializers.Serializer):
    operation = serializers.ChoiceField(choices=['suma', 'resta', 'escalar', 'comb2', 'comb3', 'dot'])

    # Dict[str, List[float]]
    vectors = serializers.DictField(
        child=serializers.ListField(child=serializers.FloatField())
    )

    # Dict[str, float]
    scalars = serializers.DictField(
        child=serializers.FloatField(), required=False
    )

    options = serializers.DictField(required=False)

    def validate(self, data):
        op = data["operation"]
        vecs = data.get("vectors") or {}
        sc = data.get("scalars") or {}

        def same_len(*vnames):
            sizes = []
            for name in vnames:
                if name not in vecs:
                    raise serializers.ValidationError(f"Falta el vector '{name}'.")
                if not isinstance(vecs[name], list) or not all(isinstance(x, (int, float)) for x in vecs[name]):
                    raise serializers.ValidationError(f"'{name}' debe ser una lista de números.")
                sizes.append(len(vecs[name]))
            if len(set(sizes)) != 1:
                raise serializers.ValidationError(f"Los vectores {', '.join(vnames)} deben tener la misma longitud.")

        if op in ['suma', 'resta']:
            same_len('u', 'v')

        elif op == "escalar":
            if "u" not in vecs or "c" not in sc:
                raise serializers.ValidationError("Para 'escalar' envía vectors.u y scalars.c.")

        elif op == "comb2":
            same_len('u', 'v')
            if "c" not in sc or "d" not in sc:
                raise serializers.ValidationError("Para 'comb2' envía scalars.c y scalars.d.")

        elif op == "comb3":
            same_len("u", "v", "w")
            if "c" not in sc or "d" not in sc:
                raise serializers.ValidationError("Para 'comb3' envía scalars.c y scalars.d.")

        elif op == "dot":
            same_len("v", "w")

        return {**data, "vectors": vecs, "scalars": sc}
