from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse
from core.models import Course, CourseContent, CourseMember, User

# Create your views here.
def index(request):
    return HttpResponse("<h1>Selamat datang di LMS Kita</h1>")


def testing(request):
    guru = User.objects.create_user(
        username="guru_1", email="guru1@gmail.com", 
        password="rahasia", first_name="Guru", last_name="Satu"
        )

    Course.objects.create(
        name="Pemrograman Python",
        description="Belajar Pemrograman Python",
        price=500000,
        teacher=guru
    )

    return HttpResponse("kosongan")


def allCourses(request):
    courses = Course.objects.all().select_related('teacher')
    data_resp = []
    for course in courses:
        record = {'id': course.id, 'name': course.name,
                  'price': course.price,
                  'teacher': {
                      'id': course.teacher.id,
                      'username': course.teacher.username,
                      'fullname': f"{course.teacher.first_name}{course.teacher.last_name}"
                  }}
        data_resp.append(record)

    return JsonResponse(data_resp, safe=False)

def userProfile(request, user_id):
    user = User.objects.get(pk=user_id)
    courses = Course.objects.filter(teacher=user)
    data_resp = {'username': user.username, 'email': user.email, 
                 'fullname': f"{user.first_name}{user.last_name}"}
    data_resp['courses'] = []
    for course in courses:
        course_data = {'id': course.id,
                       'name': course.name,
                       'description': course.description,
                       'price': course.price}
        data_resp['courses'].append(course_data)
    return JsonResponse(data_resp, safe=False)

from django.db.models import Count, Min, Max, Avg

def courseStats(request):
    courses = Course.objects.all()
    statistics = courses.aggregate(course_count=Count('*'),
                                   min_price=Min('price'),
                                   max_price=Max('price'),
                                   avg_price=Avg('price')
                                   )
    cheapest_list = Course.objects.filter(price=statistics['min_price'])
    expensive_list = Course.objects.filter(price=statistics['max_price'])
    popular_list = Course.objects.annotate(member_count=Count('coursemember'))\
                         .order_by('-member_count')[:3]
    unpopular_list = Course.objects.annotate(member_count=Count('coursemember'))\
                         .order_by('member_count')[:3]
    
    data_resp = {
        'course_count': statistics['course_count'],
        'min_price': statistics['min_price'],
        'max_price': statistics['max_price'],
        'avg_price': statistics['avg_price'],
        'cheapest': [course.name for course in cheapest_list],
        'expensive': [course.name for course in expensive_list],
        'popular': [course.name for course in popular_list],
        'unpopular': [course.name for course in unpopular_list],
    }

    return JsonResponse(data_resp, safe=False)


def user_course_stats(request):   
    users_with_courses = User.objects.annotate(course_count=Count('course')).filter(course_count__gt=0).count()  
    users_without_courses = User.objects.annotate(course_count=Count('course')).filter(course_count=0).count()  
    avg_courses_per_user = User.objects.annotate(course_count=Count('coursemember')).aggregate(Avg('course_count'))['course_count__avg']  
    top_user = User.objects.annotate(course_count=Count('coursemember')).order_by('-course_count').first()
    users_not_following_courses = User.objects.filter(coursemember__isnull=True).values_list('username', flat=True)
    data_resp = {
        'users_with_courses': users_with_courses,
        'users_without_courses': users_without_courses,
        'avg_courses_per_user': avg_courses_per_user,
        'top_user': top_user.username if top_user else 'None',
        'users_not_following_courses': list(users_not_following_courses),
    }

    return JsonResponse(data_resp, safe=False)



    