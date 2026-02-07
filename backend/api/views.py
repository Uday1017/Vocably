from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from core.models import User, Analysis
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    AnalysisSerializer, AnalysisCreateSerializer, AnalysisListSerializer
)
from .tasks import process_video_analysis

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(email=email)
        user = authenticate(request, username=user.username, password=password)
    except User.DoesNotExist:
        user = None
    
    if user is not None:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})


class AnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AnalysisCreateSerializer
        elif self.action == 'list':
            return AnalysisListSerializer
        return AnalysisSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        analysis = serializer.save(user=request.user)
        
        # Trigger async processing
        process_video_analysis.delay(analysis.id)
        
        return Response({
            'id': analysis.id,
            'message': 'Video uploaded successfully. Processing started.',
            'status': 'pending'
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'])
    def progress(self, request):
        analyses = self.get_queryset().filter(status='completed').order_by('created_at')
        
        if analyses.count() < 2:
            return Response({
                'has_progress': False,
                'message': 'Need at least 2 completed analyses to show progress'
            })
        
        progress_data = {
            'has_progress': True,
            'total_analyses': analyses.count(),
            'grammar': [a.grammar_score for a in analyses],
            'fluency': [a.fluency_score for a in analyses],
            'politeness': [a.politeness_score for a in analyses],
            'body_language': [a.body_language_score for a in analyses],
            'overall': [a.overall_score for a in analyses],
            'dates': [a.created_at.strftime('%b %d') for a in analyses],
            'improvement': {
                'grammar': round(analyses.last().grammar_score - analyses.first().grammar_score, 1),
                'fluency': round(analyses.last().fluency_score - analyses.first().fluency_score, 1),
                'politeness': round(analyses.last().politeness_score - analyses.first().politeness_score, 1),
                'overall': round(analyses.last().overall_score - analyses.first().overall_score, 1)
            }
        }
        return Response(progress_data)
