from django.contrib import admin
from .models import Question
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['counsel_id']
admin.site.register(Question, QuestionAdmin)
# Register your models here.
