from rest_framework import serializers
from .models import Survey, Question, Option, SurveyQuestion,SurveyResult

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'image', 'video']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'image', 'video', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question

class SurveyQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = SurveyQuestion
        fields = ['id', 'question']

class SurveySerializer(serializers.ModelSerializer):
    survey_questions = SurveyQuestionSerializer( many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'created_at', 'survey_questions']

class SurveyCreateSerializer(serializers.ModelSerializer):
    questions = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    new_questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'questions', 'new_questions']

    def create(self, validated_data):
        # Extract questions and new_questions data
        question_ids = validated_data.pop('questions', [])
        new_questions_data = validated_data.pop('new_questions', [])

        # Create the survey
        survey = Survey.objects.create(**validated_data)

        # Map existing questions
        for question_id in question_ids:
            question = Question.objects.get(id=question_id)
            SurveyQuestion.objects.create(survey=survey, question=question)

        # Create and map new questions
        for question_data in new_questions_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(**question_data)
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)
            SurveyQuestion.objects.create(survey=survey, question=question)

        return survey

class SurveyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResult
        fields = ['id', 'survey', 'question', 'selected_option', 'text_answer']
        read_only_fields = ['id']  # ID is read-only

    def validate(self, data):
        """Ensure that a valid option or text answer is provided."""
        question = data['question']
        if question.question_type == 'MCQ' and not data.get('selected_option'):
            raise serializers.ValidationError("An option must be selected for multiple-choice questions.")
        if question.question_type == 'TEXT' and not data.get('text_answer'):
            raise serializers.ValidationError("A text answer is required for text questions.")
        return data