from django.test import TestCase
from rest_framework.test import APIClient
from tasks.models import Task
class TaskApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    def test_list_tasks_starts_empty(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
    def test_create_task(self):
        response = self.client.post("/api/tasks/", {"title":"Learn harness","status":"todo"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 1)
    def test_invalid_status_is_rejected(self):
        response = self.client.post("/api/tasks/", {"title":"Bad task","status":"invalid"}, format="json")
        self.assertEqual(response.status_code, 400)
