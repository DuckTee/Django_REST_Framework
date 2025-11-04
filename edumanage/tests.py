from django.test import TestCase
from django.contrib.auth import get_user_model
from edumanage.models import Course, Subscription, Lesson

User = get_user_model()


class CourseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com", password="pass123"
        )

    def test_create_course(self):
        course = Course.objects.create(
            title="Python Basics", description="Основы Python", owner=self.user
        )
        self.assertEqual(course.title, "Python Basics")
        self.assertEqual(course.owner, self.user)

    def test_course_str(self):
        course = Course(title="Test Course")
        self.assertEqual(str(course), "Test Course")

    def test_owner_deletion_cascade(self):
        course = Course.objects.create(title="Course", owner=self.user)
        self.user.delete()
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="pass123"
        )
        self.course = Course.objects.create(title="Math Course", owner=self.user)

    def test_create_subscription(self):
        subscription = Subscription.objects.create(user=self.user, course=self.course)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.course, self.course)

    def test_unique_subscription(self):
        Subscription.objects.create(user=self.user, course=self.course)
        with self.assertRaises(Exception):
            Subscription.objects.create(user=self.user, course=self.course)

    def test_subscription_str(self):
        subscription = Subscription(user=self.user, course=self.course)
        expected = f"{self.user.email} → {self.course.title}"
        self.assertEqual(str(subscription), expected)

    def test_course_deletion_removes_subscription(self):
        subscription = Subscription.objects.create(user=self.user, course=self.course)
        self.course.delete()
        self.assertFalse(Subscription.objects.filter(pk=subscription.pk).exists())


class LessonModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="teacher@example.com", password="pass123"
        )
        self.course = Course.objects.create(title="Physics", owner=self.user)

    def test_create_lesson(self):
        lesson = Lesson.objects.create(
            course=self.course,
            title="Introduction",
            description="Первый урок",
            owner=self.user,
        )
        self.assertEqual(lesson.title, "Introduction")
        self.assertEqual(lesson.course, self.course)
        self.assertEqual(lesson.owner, self.user)

    def test_lesson_str(self):
        lesson = Lesson(title="Lesson 1", course=self.course)
        self.assertEqual(str(lesson), "Lesson 1 | Physics")

    def test_video_url_optional(self):
        lesson = Lesson.objects.create(
            course=self.course, title="No Video", owner=self.user
        )
        self.assertIsNone(lesson.video_url)

    def test_course_deletion_removes_lessons(self):
        lesson = Lesson.objects.create(
            course=self.course, title="Lesson", owner=self.user
        )
        self.course.delete()
        self.assertFalse(Lesson.objects.filter(pk=lesson.pk).exists())
