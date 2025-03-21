from django.db import models
from exam.models import User

class Survey(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('TEXT', 'Free Text'),
    )

    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=4, choices=QUESTION_TYPES)
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    video = models.FileField(upload_to='question_videos/', blank=True, null=True)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    image = models.ImageField(upload_to='option_images/', blank=True, null=True)
    video = models.FileField(upload_to='option_videos/', blank=True, null=True)

    def __str__(self):
        return f"{self.text} (for {self.question.text})"

class SurveyQuestion(models.Model):
    survey = models.ForeignKey(Survey, related_name='survey_questions', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='surveys', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('survey', 'question')

    def __str__(self):
        return f"{self.survey.name} - {self.question.text}"


class SurveyResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, related_name='results', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.SET_NULL)
    text_answer = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user.username} - Survey: {self.survey.name}"