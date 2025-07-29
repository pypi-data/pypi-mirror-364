from django.shortcuts import render, get_object_or_404
from .models import Question
# Create your views here.


def index(request):
    latest_questions = Question.objects.order_by("-pub_date")[:5]
    return render(request, "polls/index.html", {"latest_questions": latest_questions})

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})
