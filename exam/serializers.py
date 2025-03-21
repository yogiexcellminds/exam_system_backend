from rest_framework import serializers
from .models import User, Question, Choice, QuestionPaper, AnswerSheet, AssignedQuestionPaper
import logging
logger = logging.getLogger(__name__)
from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class CustomTokenCreateSerializer(TokenCreateSerializer):
#     user_id = serializers.IntegerField(source="user.id", read_only=True)

#     class Meta:
#         model = TokenCreateSerializer.Meta.model  # Use the base model from TokenCreateSerializer
#         fields = ['auth_token', 'user_id']  # Explicitly define the fields you want in the response

# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

# Choice serializer
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct']
    
    # Override the to_representation method
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Force 'is_correct' to always be False for this API response
        representation['is_correct'] = False
        return representation

# # Question serializer
# class QuestionSerializer(serializers.ModelSerializer):
#     choices = ChoiceSerializer(many=True)  # Use the nested serializer for choices

#     class Meta:
#         model = Question
#         fields = ['id', 'question_text', 'question_type', 'category', 'difficulty_level', 'image', 'video', 'audio', 'choices', 'created_by']

#     def create(self, validated_data):
#         # Use .get() to safely extract choices or default to an empty list
#         choices_data = validated_data.pop('choices', [])
        
#         # Create the question first
#         question = Question.objects.create(**validated_data)

#         # Loop through choices_data and create Choice objects linked to the question
#         for choice_data in choices_data:
#             Choice.objects.create(question=question, **choice_data)

#         return question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct', 'media', 'media_type']

    def validate(self, data):
        media = data.get('media', None)
        media_type = data.get('media_type', None)

        # Validate the file based on media_type
        if media and media_type:
            if media_type == 'image' and not media.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise serializers.ValidationError('Please upload a valid image file.')
            elif media_type == 'video' and not media.name.endswith(('.mp4', '.mov', '.avi')):
                raise serializers.ValidationError('Please upload a valid video file.')
            elif media_type == 'audio' and not media.name.endswith(('.mp3', '.wav', '.ogg')):
                raise serializers.ValidationError('Please upload a valid audio file.')

        return data


class QuestionSerializer(serializers.ModelSerializer):
    # Include choices as a nested serializer
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'category', 'difficulty_level', 'media', 'media_type','choices']

    def validate(self, data):
        media = data.get('media', None)
        media_type = data.get('media_type', None)

        # Validate the file based on media_type
        if media and media_type:
            if media_type == 'image' and not media.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise serializers.ValidationError('Please upload a valid image file.')
            elif media_type == 'video' and not media.name.endswith(('.mp4', '.mov', '.avi')):
                raise serializers.ValidationError('Please upload a valid video file.')
            elif media_type == 'audio' and not media.name.endswith(('.mp3', '.wav', '.ogg')):
                raise serializers.ValidationError('Please upload a valid audio file.')

        return data
    
# Question Paper serializer
class QuestionPaperSerializer(serializers.ModelSerializer):
    # questions = QuestionSerializer(many=True, read_only=True)
    questions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Question.objects.all()
    )
    class Meta:
        model = QuestionPaper
        fields = ['id', 'title', 'description', 'questions', 'created_by','is_active']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['questions'] = QuestionSerializer(instance.questions.all(), many=True).data
        return representation
    
    def create(self, validated_data):
        questions = validated_data.pop('questions', [])
        
        # Log the questions to ensure they are being passed correctly
        logger.debug(f"Questions received for QuestionPaper: {questions}")
        
        question_paper = QuestionPaper.objects.create(**validated_data)
        if questions:
            question_paper.questions.set(questions)
            logger.debug(f"Questions set for QuestionPaper ID {question_paper.id}: {question_paper.questions.all()}")
        else:
            logger.debug(f"No questions set for QuestionPaper ID {question_paper.id}")
        
        return question_paper

    # Override update method to handle Many-to-Many relationship
    def update(self, instance, validated_data):
        questions = validated_data.pop('questions', None)
        instance = super().update(instance, validated_data)
        if questions is not None:
            instance.questions.set(questions)  # Update the questions
        return instance

# Answer Sheet serializer
class AnswerSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerSheet
        fields = ['id', 'user', 'question_paper', 'answers', 'submitted_at']

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_id'] = instance.id  # Add user_id to the response
        return representation

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user-specific info to the response
        data.update({'user_id': self.user.id})
        data.update({'user_name': self.user.username})
        
        print(" user name ",self.user.username)
        return data

class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_choice_id = serializers.IntegerField()

class SubmittedAnswersSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    question_paper_id = serializers.IntegerField()
    answers = AnswerSubmissionSerializer(many=True)



class AssignTestSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    user_ids = serializers.ListField(child=serializers.IntegerField())
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

class AssignedQuestionPaperSerializer(serializers.ModelSerializer):
    # Nested serializer to display question paper details
    question_paper_title = serializers.CharField(source='question_paper.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AssignedQuestionPaper
        fields = ['id', 'question_paper', 'question_paper_title', 'user', 'username', 'start_date', 'end_date', 'is_completed']
