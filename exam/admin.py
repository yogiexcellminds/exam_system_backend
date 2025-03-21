from django.contrib import admin
from django.shortcuts import render,redirect

import csv
from django.contrib import admin
from django.shortcuts import render
from .models import Question, Choice
from .forms import QuestionCSVUploadForm
from django.contrib import messages
# Register your models here.

# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ['id','question_text', 'question_type', 'category', 'difficulty_level']

#     # Adding the custom action to the admin panel
#     actions = ['upload_questions_via_csv']

#     # Custom action to upload questions via CSV
#     def upload_questions_via_csv(self, request, queryset=None):
#         if request.method == "POST":
#             csv_file = request.FILES.get("csv_file")

#             if not csv_file or not csv_file.name.endswith('.csv'):
#                 messages.error(request, "Please upload a valid CSV file.")
#                 return redirect("..")  # Redirect to the previous page

#             decoded_file = csv_file.read().decode('utf-8').splitlines()
#             reader = csv.reader(decoded_file)

#             # Process the CSV data
#             try:
#                 for row in reader:
#                     question_text, question_type, category, difficulty_level, choice_text, is_correct = row

#                     # Create or get the question
#                     question, created = Question.objects.get_or_create(
#                         question_text=question_text,
#                         question_type=question_type,
#                         category=category,
#                         difficulty_level=difficulty_level
#                     )

#                     # Create the choice for the question
#                     Choice.objects.create(
#                         question=question,
#                         choice_text=choice_text,
#                         is_correct=is_correct.lower() == 'true'
#                     )

#                 messages.success(request, "Questions and choices imported successfully.")
#                 return redirect("..")  # Redirect back to the admin page

#             except Exception as e:
#                 messages.error(request, f"Error processing file: {str(e)}")
#                 return redirect("..")

#         # If it's not POST, render the file upload form
#         form = QuestionCSVUploadForm()
#         context = {
#             'form': form,
#             'title': "Upload Questions via CSV"
#         }
#         return render(request, "admin/csv_upload.html", context)

#     # Set the name for the custom action
#     upload_questions_via_csv.short_description = "Upload Questions via CSV"



from django.contrib import admin
from django.shortcuts import render,redirect

import csv
from django.contrib import admin
from django.shortcuts import render
from .models import Question, Choice
from .forms import QuestionCSVUploadForm
from django.contrib import messages
# Register your models here.

# Inline model for Choices
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3  # Allows adding 3 extra choices by default in the admin panel

# Admin model for Question
# @admin.register(Question)
# class QuestionAddAdmin(admin.ModelAdmin):
#     list_display = ['question_text', 'category', 'difficulty_level']
#     inlines = [ChoiceInline]  # Enable inline choice editing for each question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id','question_text', 'question_type', 'category', 'difficulty_level']

    # Adding the custom action to the admin panel
    actions = ['upload_questions_via_csv']
    inlines = [ChoiceInline]  # Inline choices for each question

    # Custom action to upload questions via CSV
    def upload_questions_via_csv(self, request, queryset=None):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")

            if not csv_file or not csv_file.name.endswith('.csv'):
                messages.error(request, "Please upload a valid CSV file.")
                return redirect("..")  # Redirect to the previous page

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)

            # Process the CSV data
            try:
                for row in reader:
                    question_text, question_type, category, difficulty_level, choice_text, is_correct = row

                    # Create or get the question
                    question, created = Question.objects.get_or_create(
                        question_text=question_text,
                        question_type=question_type,
                        category=category,
                        difficulty_level=difficulty_level
                    )

                    # Create the choice for the question
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        is_correct=is_correct.lower() == 'true'
                    )

                messages.success(request, "Questions and choices imported successfully.")
                return redirect("..")  # Redirect back to the admin page

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect("..")

        # If it's not POST, render the file upload form
        form = QuestionCSVUploadForm()
        context = {
            'form': form,
            'title': "Upload Questions via CSV"
        }
        return render(request, "admin/csv_upload.html", context)

    # Set the name for the custom action
    upload_questions_via_csv.short_description = "Upload Questions via CSV"




from django.contrib.auth.models import User
from .models import QuestionPaper, AnswerSheet

# Register the QuestionPaper model
@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'created_by']  # Customize the fields displayed in the list view

# Register the AnswerSheet model
@admin.register(AnswerSheet)
class AnswerSheetAdmin(admin.ModelAdmin):
    list_display = ['user', 'question_paper', 'question', 'selected_choice', 'is_correct', 'submitted_at']
    list_filter = ['is_correct', 'submitted_at']  # Add filters to filter answers
    search_fields = ['user__username', 'question__question_text']  # Add search capability

# If you want to manage Django's built-in User model, you can register it as well (optional)
admin.site.register(User)