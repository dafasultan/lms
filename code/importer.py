import os
import sys

# Setup Django environment
# Tambahin path ke root folder project lo
sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 3)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms.settings'

import django
django.setup()

import csv
import json
from random import randint
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from core.models import Course, CourseMember, CourseContent, Comment
import time

start_time = time.time()

# Filepath ke data dummy
filepath = './dummy_data/'

# Import User data
with open(filepath + 'user-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    for row in reader:
        if not User.objects.filter(username=row['username']).exists():
            obj_create.append(User(
                username=row['username'],
                password=make_password(row['password']),
                email=row['email'],
                first_name=row['firstname'],
                last_name=row['lastname']
            ))
    User.objects.bulk_create(obj_create)

# Import Course data
with open(filepath + 'course-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    for num, row in enumerate(reader):
        try:
            teacher = User.objects.get(pk=int(row['teacher']))
            if not Course.objects.filter(pk=num + 1).exists():
                obj_create.append(Course(
                    name=row['name'],
                    price=row['price'],
                    description=row['description'],
                    teacher=teacher
                ))
        except User.DoesNotExist:
            print(f"User with id {row['teacher']} does not exist. Skipping this course.")
    Course.objects.bulk_create(obj_create)

# Import CourseMember data
with open(filepath + 'member-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    for num, row in enumerate(reader):
        try:
            course = Course.objects.get(pk=int(row['course_id']))
            user = User.objects.get(pk=int(row['user_id']))
            if not CourseMember.objects.filter(pk=num + 1).exists():
                obj_create.append(CourseMember(
                    course_id=course,
                    user_id=user,
                    roles=row['roles']
                ))
        except (Course.DoesNotExist, User.DoesNotExist) as e:
            print(f"Skipping CourseMember: {e}")
    CourseMember.objects.bulk_create(obj_create)

# Import CourseContent data
with open(filepath + 'contents.json') as jsonfile:
    contents = json.load(jsonfile)
    obj_create = []
    for num, row in enumerate(contents):
        try:
            course = Course.objects.get(pk=int(row['course_id']))
            if not CourseContent.objects.filter(pk=num + 1).exists():
                obj_create.append(CourseContent(
                    course_id=course,
                    video_url=row['video_url'],
                    name=row['name'],
                    description=row['description']
                ))
        except Course.DoesNotExist:
            print(f"Course with id {row['course_id']} does not exist. Skipping this content.")
    CourseContent.objects.bulk_create(obj_create)

# Import Comment data
with open(filepath + 'comments.json') as jsonfile:
    comments = json.load(jsonfile)
    obj_create = []
    for num, row in enumerate(comments):
        try:
            content = CourseContent.objects.get(pk=int(row['content_id']))
            user_id = int(row['user_id'])
            if user_id > 50:
                user_id = randint(5, 40)
            user = User.objects.get(pk=user_id)
            if not Comment.objects.filter(pk=num + 1).exists():
                obj_create.append(Comment(
                    content_id=content,
                    user_id=user,
                    comment=row['comment']
                ))
        except (CourseContent.DoesNotExist, User.DoesNotExist) as e:
            print(f"Skipping Comment: {e}")
    Comment.objects.bulk_create(obj_create)

print(f"--- {time.time() - start_time} seconds ---")
