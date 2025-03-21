from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets
from .models import Survey, Question, SurveyResult
from .serializers import SurveyCreateSerializer,SurveySerializer, QuestionSerializer, SurveyResultSerializer,SurveyCreateSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class SurveyViewSet(viewsets.ModelViewSet):
    # queryset = Survey.objects.all()
    # serializer_class = SurveySerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Survey.objects.all()
    serializer_class = SurveyCreateSerializer
    permission_classes = [IsAuthenticated]

class SurveyGetViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SurveyResultViewSet(viewsets.ModelViewSet):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = [DjangoFilterBackend]  # Enable filtering
    # filterset_fields = ['id','survey']  # Allow filtering by 'user'

    def get_queryset(self):
        """
        Optionally restricts the returned survey results to a given user,
        by filtering against a 'user' query parameter in the URL.
        """
        print(' --- ',self.request.query_params.get('id'))
        queryset = super().get_queryset()
        

        user_id = self.request.query_params.get('id')
        print(' user_id ',user_id)
        if user_id:
            queryset = queryset.filter(user__id=user_id)
            answers_list = list(queryset)
            print(' queryset',answers_list)
        return queryset
    def perform_create(self, serializer):
        # Automatically set the user from the authenticated request
        serializer.save(user=self.request.user)


