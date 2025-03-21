from django.shortcuts import render,redirect
import csv

# Create your views here.
from rest_framework import viewsets
from .models import User, Question, Choice, QuestionPaper, AnswerSheet
from .serializers import (
    UserSerializer, QuestionSerializer, ChoiceSerializer, 
    AnswerSheetSerializer,QuestionPaperSerializer,
    SubmittedAnswersSerializer)

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .forms import QuestionCSVUploadForm
from django.contrib import messages
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class CustomQuestionPagination(PageNumberPagination):
    page_size = 10  # Items per page for this specific view
    page_size_query_param = 'page_size'  # Allows the client to set page size via a query param
    max_page_size = 100  # Maximum page size allowed

# User Viewset
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Question Viewset
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    # Override the perform_create method to automatically set 'created_by'
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Choice Viewset
class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

# Question Paper Viewset
class QuestionPaperViewSet(viewsets.ModelViewSet):
    queryset = QuestionPaper.objects.all()
    serializer_class = QuestionPaperSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# AnswerSheet Viewset
class AnswerSheetViewSet(viewsets.ModelViewSet):
    queryset = AnswerSheet.objects.all()
    serializer_class = AnswerSheetSerializer


class QuestionPaperDetailView(generics.RetrieveAPIView):
    queryset = QuestionPaper.objects.all()
    serializer_class = QuestionPaperSerializer
    permission_classes = [IsAuthenticated]

class ActiveQuestionPaperDetailViewSet(viewsets.ModelViewSet):

    queryset = QuestionPaper.objects.filter(is_active=True)
    serializer_class = QuestionPaperSerializer
    permission_classes = [IsAuthenticated]
 

# View to get only active Question Papers
class ActiveQuestionPaperListView(generics.ListAPIView):
    serializer_class = QuestionPaperSerializer

    def get_queryset(self):
        return QuestionPaper.objects.filter(is_active=True)    

def upload_questions(request):
    if request.method == "POST":
        form = QuestionCSVUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['csv_file']

            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('upload_questions')  # Redirect back to the upload page

            # Decode the CSV file
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)

                # Process each row in the CSV file
                for row in reader:
                    question_text, question_type, category, difficulty_level, choice_text, is_correct = row

                    # Create or get the question, and set the 'created_by' field to the current user
                    question, created = Question.objects.get_or_create(
                        question_text=question_text,
                        question_type=question_type,
                        category=category,
                        difficulty_level=difficulty_level,
                        created_by=request.user  # Set the current user as the creator
                    )

                    # Create the choice for the question
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        is_correct=is_correct.lower() == 'true'
                    )

                messages.success(request, "Questions and choices imported successfully.")
                return redirect('upload_questions')  # Redirect back to the upload page

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect('upload_questions')

    else:
        form = QuestionCSVUploadForm()

    return render(request, 'upload_questions.html', {'form': form})



class FilterQuestionsAPI(generics.ListAPIView):
    serializer_class = QuestionSerializer
    pagination_class = CustomQuestionPagination  # Use custom pagination class

    def get_queryset(self):
        queryset = Question.objects.all()

        category = self.request.query_params.get('category', None)
        difficulty_level = self.request.query_params.get('difficulty_level', None)

        if category:
            queryset = queryset.filter(category=category)
        if difficulty_level:
            queryset = queryset.filter(difficulty_level=difficulty_level)

        return queryset
    


class CheckAnswersAPIView(APIView):
    def post(self, request):
        # Deserialize and validate the submitted data
        serializer = SubmittedAnswersSerializer(data=request.data)
        if serializer.is_valid():
            results = []
            user_id = serializer.validated_data['user_id']
            question_paper_id = serializer.validated_data['question_paper_id']
            answers_data = serializer.validated_data['answers']

            # Fetch the user and question paper
            try:
                user = User.objects.get(id=user_id)
                question_paper = QuestionPaper.objects.get(id=question_paper_id)
            except (User.DoesNotExist, QuestionPaper.DoesNotExist):
                return Response({"error": "Invalid user or question paper."}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate through each submitted answer
            for answer_data in answers_data:
                question_id = answer_data['question_id']
                selected_choice_id = answer_data['selected_choice_id']

                # Fetch the question and the selected choice
                try:
                    question = Question.objects.get(id=question_id)
                    selected_choice = Choice.objects.get(id=selected_choice_id, question=question)
                except (Question.DoesNotExist, Choice.DoesNotExist):
                    return Response({"error": f"Invalid question or choice."}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the selected choice is the correct one
                is_correct = selected_choice.is_correct

                # Store the result in the AnswerSheet table
                AnswerSheet.objects.create(
                    user=user,
                    question_paper=question_paper,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )

                # Add the result for this question
                results.append({
                    'question_id': question_id,
                    'question_text': question.question_text,
                    'selected_choice_id': selected_choice_id,
                    'selected_choice_text': selected_choice.choice_text,
                    'is_correct': is_correct
                })

            # Return the results to the user
            return Response({"results": results}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CheckAnswersAPIView(APIView):
    def post(self, request):
        # Deserialize and validate the submitted data
        serializer = SubmittedAnswersSerializer(data=request.data)
        if serializer.is_valid():
            results = []
            user_id = serializer.validated_data['user_id']
            question_paper_id = serializer.validated_data['question_paper_id']
            answers_data = serializer.validated_data['answers']

            # Fetch the user and question paper
            try:
                user = User.objects.get(id=user_id)
                question_paper = QuestionPaper.objects.get(id=question_paper_id)
            except (User.DoesNotExist, QuestionPaper.DoesNotExist):
                return Response({"error": "Invalid user or question paper."}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate through each submitted answer
            for answer_data in answers_data:
                question_id = answer_data['question_id']
                selected_choice_id = answer_data['selected_choice_id']

                # Fetch the question and the selected choice
                try:
                    question = Question.objects.get(id=question_id)
                    selected_choice = Choice.objects.get(id=selected_choice_id, question=question)
                except (Question.DoesNotExist, Choice.DoesNotExist):
                    return Response({"error": f"Invalid question or choice."}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the selected choice is the correct one
                is_correct = selected_choice.is_correct

                # Store the result in the AnswerSheet table
                AnswerSheet.objects.create(
                    user=user,
                    question_paper=question_paper,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )

                # Add the result for this question
                results.append({
                    'question_id': question_id,
                    'question_text': question.question_text,
                    'selected_choice_id': selected_choice_id,
                    'selected_choice_text': selected_choice.choice_text,
                    'is_correct': is_correct
                })

            # Return the results to the user
            return Response({"results": results}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from django.urls import get_resolver
from rest_framework.response import Response
from rest_framework.views import APIView

class ListAllAPIsView(APIView):
    """
    API View to list all registered API URLs.
    """

    def get(self, request):
        url_resolver = get_resolver()
        all_urls = []
        for pattern in url_resolver.url_patterns:
            if hasattr(pattern, 'url_patterns'):
                for subpattern in pattern.url_patterns:
                    all_urls.append(str(subpattern.pattern))
            else:
                all_urls.append(str(pattern.pattern))
        return Response({"api_endpoints": all_urls})