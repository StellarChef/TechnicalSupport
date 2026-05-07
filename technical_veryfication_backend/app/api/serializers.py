from rest_framework import serializers


class VerificationRequestSerializer(serializers.Serializer):
    issue_topic = serializers.CharField()
    photos = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=True, default=list
    )
    damage_description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    use_ai = serializers.BooleanField(required=False, default=True)


class CostEstimationRequestSerializer(serializers.Serializer):
    input_data = serializers.DictField()
    search_results = serializers.CharField(required=False, allow_blank=True, default="")
    use_ai = serializers.BooleanField(required=False, default=True)


class CreateCaseRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    photos = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=True, default=list
    )
    damage_description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    search_results = serializers.CharField(required=False, allow_blank=True, default="")
    use_ai = serializers.BooleanField(required=False, default=True)
