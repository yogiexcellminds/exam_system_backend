from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    def __str__(self):
        return self.username
    


class Question(models.Model):
    QUESTION_TYPES = [('mcq', 'Multiple Choice'), ('text', 'Text Answer')]
    CATEGORY_CHOICES = [('math', 'Math'), ('science', 'Science'), ('geography', 'Geography'), ('testing', 'Testing')]
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)

    # Single media field for image, video, and audio
    media = models.FileField(upload_to='question_media/', blank=True, null=True)

    # Field to specify the type of media
    media_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video'), ('audio', 'Audio')], blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def clean(self):
        if self.media and self.media_type:
            if self.media_type == 'image' and not self.media.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise ValidationError('Please upload a valid image file.')
            elif self.media_type == 'video' and not self.media.name.endswith(('.mp4', '.mov', '.avi')):
                raise ValidationError('Please upload a valid video file.')
            elif self.media_type == 'audio' and not self.media.name.endswith(('.mp3', '.wav', '.ogg')):
                raise ValidationError('Please upload a valid audio file.')
        elif self.media and not self.media_type:
            raise ValidationError('You must specify the media type if a file is uploaded.')

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    MEDIA_TYPES = [('image', 'Image'), ('video', 'Video'), ('audio', 'Audio')]

    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    media = models.FileField(upload_to='media_files/', blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, blank=True, null=True)

    def clean(self):
        if self.media and self.media_type:
            if self.media_type == 'image' and not self.media.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise ValidationError('Please upload a valid image file.')
            elif self.media_type == 'video' and not self.media.name.endswith(('.mp4', '.mov', '.avi')):
                raise ValidationError('Please upload a valid video file.')
            elif self.media_type == 'audio' and not self.media.name.endswith(('.mp3', '.wav', '.ogg')):
                raise ValidationError('Please upload a valid audio file.')
        elif self.media and not self.media_type:
            raise ValidationError('You must specify the media type if a file is uploaded.')

    def __str__(self):
        return self.choice_text

# Question Paper model
class QuestionPaper(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    questions = models.ManyToManyField(Question)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=False)
     # Other relevant fields for the test
    duration = models.IntegerField(help_text="Duration of the test in minutes",default=30)

    def __str__(self):
        return self.title
# Answer Sheet model
# class AnswerSheet(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
#     answers = models.JSONField()  # To store answers for all questions in JSON format
#     submitted_at = models.DateTimeField(auto_now_add=True)


# Model to store user submissions

class AnswerSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE,default=0)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE,default=0)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)


class AssignedQuestionPaper(models.Model):
    question_paper = models.ForeignKey("QuestionPaper", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.test.title} assigned to {self.user.username}"