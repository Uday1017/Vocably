from rest_framework import serializers
from core.models import User, Analysis

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class AnalysisSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'user', 'user_email', 'video', 'filename', 'status',
            'transcript', 'grammar_score', 'fluency_score', 'politeness_score',
            'body_language_score', 'overall_score', 'detailed_feedback',
            'video_stats', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'transcript', 'grammar_score', 'fluency_score',
            'politeness_score', 'body_language_score', 'overall_score',
            'detailed_feedback', 'video_stats', 'created_at', 'updated_at', 'completed_at'
        ]


class AnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ['video', 'filename']
    
    def validate_video(self, value):
        if not value.name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            raise serializers.ValidationError("Invalid video format. Supported: MP4, AVI, MOV, MKV")
        if value.size > 100 * 1024 * 1024:  # 100MB
            raise serializers.ValidationError("Video file too large. Maximum size: 100MB")
        return value


class AnalysisListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = [
            'id', 'filename', 'status', 'grammar_score', 'fluency_score',
            'politeness_score', 'body_language_score', 'overall_score', 'created_at'
        ]
