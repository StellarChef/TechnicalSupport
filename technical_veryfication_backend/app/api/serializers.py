from rest_framework import serializers


class VerificationRequestSerializer(serializers.Serializer):
    issue_topic = serializers.CharField()
    photos = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=True, default=list
    )
    damage_description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )


class CostEstimationRequestSerializer(serializers.Serializer):
    input_data = serializers.DictField()
    search_results = serializers.CharField(required=False, allow_blank=True, default="")
