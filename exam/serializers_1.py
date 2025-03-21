from rest_framework import serializers
from .models import QuestionPaper, Question, Choice

# Serializer for Choices
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct']  # Exclude 'is_correct' if needed for students
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Force 'is_correct' to always be False for this API response
        representation['is_correct'] = False
        return representation
# Serializer for Questions
class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)  # Include nested choices

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'category', 'difficulty_level', 'choices']

# Serializer for Question Papers
class QuestionPaperSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)  # Nested questions with their choices

    class Meta:
        model = QuestionPaper
        fields = ['id', 'title', 'description', 'questions', 'created_by']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['questions'] = QuestionSerializer(instance.questions.all(), many=True).data
        return representation