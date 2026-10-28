from rest_framework import serializers
from .models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField()
    course_title = serializers.ReadOnlyField()
    organization_name = serializers.ReadOnlyField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'student_name', 'course_title',
            'organization_name', 'policy_version', 'status', 'download_url', 'issued_at'
        ]

    def get_download_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None

class CertificatePublicVerifySerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField()
    course_title = serializers.ReadOnlyField()
    organization_name = serializers.ReadOnlyField()

    class Meta:
        model = Certificate
        fields = [
            'certificate_number', 'student_name', 'course_title',
            'organization_name', 'status', 'issued_at'
        ]
