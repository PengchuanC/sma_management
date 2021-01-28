from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from questionnaire.models import Questions, Client, Result, ResultInfo

from itertools import groupby
from collections import OrderedDict
from dateutil.parser import parse


# 获取问卷列表
def get_questions():
    questions = Questions.objects.order_by('question_id')
    questions = sorted(questions, key=lambda x: x.question_id)
    ret = OrderedDict()
    quest: Questions
    for quest in questions:
        sub = quest.subject
        if sub not in ret:
            ret[sub] = []
        choices = [[x.choice_id, x.text] for x in quest.choices]
        ret[sub].append({'id': quest.question_id, 'quest': quest.text, 'choice': choices})
    return ret


def questionnaire(request):
    user = request.user
    if not request.user.is_authenticated:
        user = None
    return render(request, 'questionnaire/index.html', {'user': user})


def login_page(request):
    return render(request, 'questionnaire/login.html')


def logout_user(request):
    logout(request)
    return render(request, 'questionnaire/index.html')


def login_user(request):
    if 'username' not in request.POST:
        return render(request, 'questionnaire/login.html', {'status': -1})
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return render(request, 'questionnaire/index.html')
    return render(request, 'questionnaire/login.html', {'status': -1})


def create(request):
    """问卷页路由"""
    ret = get_questions()
    return render(request, 'questionnaire/create.html', {'questions': ret})


def view_questionnaire(request):
    """已填写问卷列表"""
    questions = ResultInfo.objects.order_by('client__name', '-date')
    questions = sorted(questions, key=lambda x: x.client.name)
    data = groupby(questions, key=lambda x: x.client.name)
    data = [[x[0], list(x[1])] for x in data]
    return render(request, 'questionnaire/view.html', {'questions': data})


def modify(request, ri):
    """修改问卷"""
    ri = ResultInfo.objects.filter(id=ri).first()
    ret = get_questions()
    user = request.user
    results = Result.objects.filter(info=ri).order_by('question_id')
    results = {x.question_id: x.choice_id for x in results}
    questions = OrderedDict()
    for x in ret:
        questions[x] = []
        for y in ret[x]:
            choice = results.get(y['id'])
            y['checked'] = choice
            questions[x].append(y)
    return render(request, 'questionnaire/modify.html', {'user': user, 'info': ri, 'questions': questions})


def save(request):
    """保存问卷"""
    finish = True
    success = False
    msg = None
    data = request.POST
    data = {x: y for x, y in data.items()}
    name, sales = data.pop('clientName'), data.pop('salesName')
    account, date = data.pop('clientAccount'), data.pop('signDate')
    date = parse(date).date()
    associate_name = data.pop('associateName') or None
    associate_account = data.pop('associateAccount') or None
    client = Client.objects.filter(account=account)
    if not client.exists():
        client = Client(name=name, account=account, associate_name=associate_name, associate_account=associate_account)
        client.save()
    if len(data) != len(Questions.objects.all()):
        msg = '问卷中存在没有填写的问题，请返回检查问题'
    else:
        client = Client.objects.get(account=account)
        ri = ResultInfo.objects.filter(client=client, date=date).first()
        if ri:
            info = ResultInfo.objects.get(client=client, date=date)
            for x in data:
                question_id, choice_id = x.split('.')
                Result.objects.update_or_create(info=info, question_id=question_id, choice_id=choice_id)
            success = True
        else:
            info = ResultInfo(client=client, sales=sales, date=date)
            info.save()
            results = []
            for x in data:
                question_id, choice_id = x.split('.')
                result = Result(info=info, question_id=question_id, choice_id=choice_id)
                results.append(result)
            Result.objects.bulk_create(results)
            success = True
    info = ResultInfo.objects.filter(client=client, date=date).first()
    ri = info.id if info else 1
    return render(request, 'questionnaire/create.html', {'finished': finish, 'success': success, 'msg': msg, 'ri': ri})


def result_notify(request):
    """业务投资测评评估结果告知书"""
    return render(request, 'questionnaire/result.html')
