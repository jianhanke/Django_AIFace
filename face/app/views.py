from django.shortcuts import render
import urllib, urllib.request, sys
import ssl
import base64
import cv2
import json
import uuid

from django.http import  HttpResponse

def home(request):
    return render(request,'app/home.html',{'Hello':'Hello'} )

def index(request):
    return render(request,'app/index.html')

def upload(request):

    img=request.FILES.get('img',None)
    if not img:
        return HttpResponse('还没有上传图片')

    img_name=str(uuid.uuid1())+'.jpg'
    filepath='media/'+img_name
    with open(filepath,'wb') as f:
        for line in img.chunks():
            f.write(line)
    persons=parse_info(filepath)
    return render(request,'app/index.html',{"img":img_name,"persons":persons})


def get_access_token():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=QOBK3IBizVXiEE0Rq7BYfUcU&client_secret=i0ooPky10RcoGDjdXOAxfmO8xG2Bz2lh'
    request = urllib.request.Request(url=host, headers={'Content-Type': 'application/json', 'charset': 'UTF-8'})
    response = urllib.request.urlopen(request)
    content = response.read()
    content = bytes.decode(content)
    content = json.loads(content)
    return content['access_token']


def get_image_byte(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read())


def get_info(filepath):
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
    img = get_image_byte(filepath)
    params = {  # 请求参数
        "image": str(img, 'utf-8'),
        "image_type": "BASE64",
        "max_face_num": '10',  # 最多识别10人，超过不出错
        "face_field": "faceshape,facetype,age,beauty,gender,beauty,race,emotion",
    }
    data = urllib.parse.urlencode(params).encode("utf-8")
    access_token = get_access_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {'Content-Type': 'application/json'}
    request = urllib.request.Request(url=request_url, data=data, headers=headers)
    response = urllib.request.urlopen(request)
    content = response.read()
    content = bytes.decode(content)
    info = json.loads(content)
    return info

def parse_info(filepath):
    info = get_info(filepath)
    nums = info['result']['face_num']
    img = cv2.imread(filepath)
    persons = []
    for i in range(0, nums):
        age = info['result']['face_list'][i]['age']
        sex = info['result']['face_list'][i]['gender']['type']
        beauty = info['result']['face_list'][i]['beauty']
        race = info['result']['face_list'][i]['race']['type']
        emotion = info['result']['face_list'][i]['emotion']['type']
        if sex == 'male':
            sex = '男'
        else:
            sex = '女'
        if race == 'yellow':
            race = '黄皮肤'
        elif (race == 'while'):
            race = '白皮肤'
        elif race == 'black':
            race = '黑皮肤'
        else:
            race = '未知'
        if emotion == 'angry':
            emotion = '愤怒'
        elif emotion == 'disgust':
            emotion = '厌恶'
        elif emotion == 'fear':
            emotion = '恐惧'
        elif emotion == 'happy':
            emotion = '高兴'
        else :
            emotion = '无情绪'
        person = []
        person.append(age)
        person.append(sex)
        person.append(beauty)
        person.append(race)
        person.append(emotion)
        persons.append(person)
        location = info['result']['face_list'][i]['location']
        left_top = (location['left'], location['top'])
        right_bottom = (left_top[0] + location['width'], left_top[1] + location['height'])
        left_top = (int(left_top[0]), int(left_top[1]))
        right_bottom = (int(right_bottom[0]), int(right_bottom[1]))
        cv2.rectangle(img, left_top, right_bottom, (0, 0, 255), 2)
    cv2.imwrite(filepath, img)
    return persons