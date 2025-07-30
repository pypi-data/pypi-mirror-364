from django.http import JsonResponse
from rest_framework import serializers

from .paginator import PaginationData
from stupa.exceptions import ResponseEnum


class SkillsPeResonse:
    def __new__(self,
                response_type: ResponseEnum,
                data: dict | serializers.Serializer | serializers.ModelSerializer = None,
                pagination_data: PaginationData = None,
                ) -> JsonResponse:

        response_data = {"message": response_type.message,
                         "response_code": response_type.response_code}
        if data:
            response_data["data"] = data.data if hasattr(
                data, 'data') else data
        if pagination_data:
            response_data["pagination"] = pagination_data
        return JsonResponse(response_data, status=response_type.status_code)
