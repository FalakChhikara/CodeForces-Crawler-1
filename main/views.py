from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
import re
from urllib.request import urlopen
from .forms import HandleForm
from django.views.generic import TemplateView
import requests


def home(request):
    if request.method == 'POST':
        form = HandleForm(request.POST)
        if form.is_valid():
            handle = form.cleaned_data.get('handle')
            return redirect('/who/' + handle)
    else:
        form = HandleForm()

    return render(request, 'home.html', {'form': form})


def who(request, handle):
    context = {
        'handle': handle,
    }
    return render(request, 'options.html', context)


def submission(request, handle):
    friend = handle
    p_link = "https://codeforces.com/api/user.status?handle="
    r = requests.get(p_link + friend)
    data = r.json()
    accepted = 0
    wrong_answer = 0
    time_exceed = 0
    runtime_error = 0
    hacked = 0
    compilation_error = 0
    submissions = {}
    today = date.today()
    for rows in data['result']:
        time = rows['creationTimeSeconds']
        s_day = datetime.fromtimestamp(time).date()
        days = (today - s_day).days
        week = days // 7
        day = days % 7 + 1
        if week <= 3:
            if submissions.get(week) is None:
                submissions[week] = {day: 1}
            else:
                dic = submissions[week]
                if dic.get(day) is None:
                    dic[day] = 1
                else:
                    dic[day] += 1
        if rows.get('verdict') is not None:
            verdict = rows['verdict']
            if verdict == "OK":
                accepted += 1
            elif verdict == "HACKED":
                hacked += 1
            elif verdict == "WRONG_ANSWER":
                wrong_answer += 1
            elif verdict == "TIME_LIMIT_EXCEEDED":
                time_exceed += 1
            elif verdict == "RUNTIME_ERROR":
                runtime_error += 1
            else:
                compilation_error += 1

    for key in submissions:
        dic = submissions[key]
        for i in range(1, 8):
            if dic.get(i) is None:
                dic[i] = 0

    context = {
        'handle': handle,
        'accepted': accepted,
        'hacked': hacked,
        'runtime_error': runtime_error,
        'wrong_answer': wrong_answer,
        'time_exceed': time_exceed,
        'compilation_error': compilation_error,
    }
    for key in submissions:
        dic = submissions[key]
        for i in range(1, 8):
            context['day' + str(key) + str(i)] = dic[i]
    print(context)
    return render(request, "sub_stats.html", context)


def contest(request, handle):
    page_url = "https://codeforces.com/api/user.rating?handle=" + handle
    r = requests.get(page_url)
    data = r.json()
    contests = []
    ranks = []
    for i in data['result']:
        contests.append(i['contestId'])
        ranks.append(i['rank'])
    context = {
        'handle': handle,
        'contests': contests,
        'ranks': ranks
    }

    return render(request, "contest_stats.html", context)