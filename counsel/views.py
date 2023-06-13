#질문 목록 조회
from django.shortcuts import render, get_object_or_404, redirect # 검색 조건을 기반으로 객체를 가져오는 함수입니다. 객체가 존재하지 않을 경우
from .models import Question                                                               #404 에러 페이지를 반환합니다.
from datetime import timezone
from .forms import QuestionForm


def index(request):
    
    """
    
    counsel 목록출력
    """
    
    question_list = Question.objects.order_by('-user_id')# Question 모델의 객체들을 user_id를 기준으로 내림차순으로 조회합니다.
    context = {'question_list': question_list}
    return render(request, 'counsel/question_list.html', context)# counsel/question_list.html 템플릿에 question_list를 전달하여 렌더링합니다.



def detail(request, question_id):
    
    """
    
    counsel 내용출력
    """

    question = Question.objects.get(id=question_id) # question_id에 해당하는 Question 객체를 조회합니다.
    context = {'question': question}
    return render(request, 'counsel/question_detail.html', context) # counsel/question_detail.html 템플릿에 question을 전달하여 렌더링합니다.

def user_id(request, question_id):
    
    """
    
    counsel 댓글 등록
    """
    
    question = get_object_or_404(Question, pk=question_id)#모델에 주어진 question_id에 해당하는 객체를 조회
                                                          #만약 객체가 존재하지 않을 때 404에러를 반환하는 의미 
    question.user_id(content=request.POST.get('content'),
                     user_id=timezone.now()) # POST 요청 시 콘텐츠라는 데이터를 가져옴
    
    return redirect('counsel:detail', question_id=question_id)
