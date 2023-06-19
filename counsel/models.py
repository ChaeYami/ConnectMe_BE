from django.db import models

class Question(models.Model):
    counsel_id= models.CharField(max_length=200)# 질문의 고유한 식별자를 나타내는 문자열 필드
    content = models.TextField()# 질문 내용을 담는 긴 텍스트 필드
    user_id = models.DateTimeField() # 질문 작성자의 날짜와 시간 정보를 담는 필드

    
     # Question 객체가 문자열로 표현될 때 counsel_id를 반환하는 메서드

    def __str__(self):
        return self.counsel_id
    
class Answer(models.Model):
    question= models.ForeignKey(Question, on_delete=models.CASCADE)# 질문의 고유한 식별자를 나타내는 문자열 필드
    content = models.TextField()# 질문 내용을 담는 긴 텍스트 필드
    user_id = models.DateTimeField() # 질문 작성자의 날짜와 시간 정보를 담는 필드
    
   