import datetime
from random import choice
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.db import transaction

from . import models


images = [
    'https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fdik.img.kttpdq.com%2Fpic%2F40%2F27947%2F89a448f7077194f1.jpg&refer=http%3A%2F%2Fdik.img.kttpdq.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1614336555&t=da62c4faae11de87cb5c4c771273f651',
    'https://ss0.bdstatic.com/70cFvHSh_Q1YnxGkpoWK1HF6hhy/it/u=2164149574,2112298220&fm=26&gp=0.jpg'
]


def get_questions():
    questions = models.Questions.objects.order_by('question_id')
    questions = sorted(questions, key=lambda x: x.question_id)
    ret = []
    quest: models.Questions
    for quest in questions:
        q = {
            'question': quest.text,
            'choices': [x.text for x in quest.choices],
            'img': choice(images)
        }
        ret.append(q)
    return ret


def home(request):
    questions = get_questions()
    data = []
    for x in questions:
        direction = 'col'
        for y in x['choices']:
            if len(y) > 30:
                direction = 'row'
                break
        x['direction'] = direction
        data.append(x)
    context = {'data': data}
    return render(request, 'questionnaire_new/content.html', context)


def welcome(request):
    """进入欢迎页面"""
    return render(request, 'questionnaire_new/index.html')


def post_authenticate(request):
    """认证页面"""
    return render(request, 'questionnaire_new/authenticate.html', {'name': '', 'mobile': '', 'show': False})


def authenticate(request):
    """客户登录认证

    主要认证方式为客户名+手机号码认证方式
    """
    params = request.POST
    name = params.get('name')
    mobile = params.get('mobile')
    user = models.Client.objects.filter(name=name, mobile=mobile).first()
    if not user:
        return render(request, 'questionnaire_new/authenticate.html', {'name': name, 'mobile': mobile, 'show': True})
    admin = User.objects.first()
    setattr(request, 'name', name)
    login(request, admin)
    return redirect(to='/question/home/')


def submit(request):
    if not request.user.is_authenticated:
        return JsonResponse({'code': -1, 'msg': '用户尚未登录'})

    results = request.POST.getlist('result')
    username = request.POST.get('name')
    client = models.Client.objects.filter(name=username).first()
    date = datetime.date.today()
    sales = '占位'
    with transaction.atomic():
        ri = models.ResultInfo(client=client, date=date, sales=sales)
        ri.save()
        results_ = []
        for q_id, c_id in enumerate(results):
            q_id += 1
            result = models.Result(info=ri, question_id=q_id, choice_id=c_id)
            results_.append(result)
        models.Result.objects.bulk_create(results_)
    return JsonResponse({'code': 0, 'msg': '保存成功'})


def success(request):
    """提交成功"""
    return render(request, 'questionnaire_new/result.html')
