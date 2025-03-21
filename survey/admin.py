from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Survey, Question, Option, SurveyQuestion, SurveyResult

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1  # Number of empty option fields shown initially

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type']
    inlines = [OptionInline]  # Allows adding options within the Question admin page
    search_fields = ['text']
    list_filter = ['question_type']

class SurveyQuestionInline(admin.TabularInline):
    model = SurveyQuestion
    extra = 1  # Number of empty survey-question fields initially

class SurveyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    inlines = [SurveyQuestionInline]  # Allows mapping questions to surveys within the Survey admin page
    search_fields = ['name', 'description']
    ordering = ['created_at']

class SurveyResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'survey', 'question', 'selected_option', 'text_answer', 'submitted_at']
    search_fields = ['user__username', 'survey__name', 'question__text']
    list_filter = ['survey', 'submitted_at']

# Registering models in the admin panel
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option)
admin.site.register(SurveyResult, SurveyResultAdmin)