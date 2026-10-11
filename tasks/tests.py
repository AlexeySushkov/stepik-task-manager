from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from tasks.models import Task


class TaskModelTests(TestCase):
    """Positive and negative scenarios for the Task model."""

    def test_create_task_default_status(self):
        task = Task.objects.create(title="New task")
        self.assertEqual(task.status, Task.Status.TODO)

    def test_create_task_with_due_date(self):
        task = Task.objects.create(
            title="With deadline",
            due_date=date(2026, 6, 1),
        )
        self.assertEqual(task.due_date, date(2026, 6, 1))

    def test_create_task_with_all_fields(self):
        task = Task.objects.create(
            title="Full task",
            description="Some details",
            status=Task.Status.IN_PROGRESS,
            due_date=date(2026, 12, 31),
        )
        self.assertEqual(task.title, "Full task")
        self.assertEqual(task.status, Task.Status.IN_PROGRESS)
        self.assertIsNotNone(task.created_at)

    def test_str_method(self):
        task = Task(title="Summary title")
        self.assertEqual(str(task), "Summary title")

    def test_ordering_descending(self):
        # time.sleep ensures different created_at values so ordering is deterministic
        import time

        _ = Task.objects.create(title="First")
        time.sleep(0.01)
        second = Task.objects.create(title="Second")
        # Meta.ordering = ["-created_at"] → newest first
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[-1].title, "First")   # oldest at the end
        self.assertEqual(tasks[0].pk, second.pk)     # newest at the front

    def test_create_task_without_title_fails(self):
        from django.core.exceptions import ValidationError

        # CharField(max_length=200) without blank=False defaults to blank=False,
        # so full_clean() should reject empty strings
        task = Task(title="")
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_all_valid_statuses_accepted(self):
        for status in Task.Status.values:
            task = Task.objects.create(title=f"Task with {status}", status=status)
            self.assertEqual(task.status, status)


class TaskApiTests(TestCase):
    """Positive and negative scenarios for the Task API."""

    def setUp(self):
        self.client = APIClient()

    # -- list --

    def test_list_tasks_starts_empty(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_tasks_returns_items(self):
        _ = Task.objects.create(title="Alpha")
        _ = Task.objects.create(title="Beta")
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        # First item is the one with the latest created_at (or highest PK)
        self.assertIn(response.data[0]["title"], ["Alpha", "Beta"])

    def test_list_task_has_all_fields(self):
        Task.objects.create(
            title="Fields check",
            description="Details here",
            status=Task.Status.DONE,
            due_date=date(2026, 3, 15),
        )
        response = self.client.get("/api/tasks/")
        keys = set(response.data[0].keys())
        expected = {"id", "title", "description", "status", "priority", "due_date", "created_at"}
        self.assertEqual(keys, expected)

    # -- retrieve --

    def test_retrieve_single_task(self):
        task = Task.objects.create(title="Retrieve me")
        response = self.client.get(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Retrieve me")

    # -- create --

    def test_create_task(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": "Learn harness", "status": "todo"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_with_all_fields(self):
        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Complete task",
                "description": "Long description",
                "status": "done",
                "due_date": "2026-09-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(pk=response.data["id"])
        self.assertEqual(task.description, "Long description")
        self.assertEqual(task.status, Task.Status.DONE)

    def test_create_task_defaults_status_when_not_provided(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": "No status"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.get().status, Task.Status.TODO)

    def test_create_task_without_title_returns_400(self):
        response = self.client.post(
            "/api/tasks/",
            {"description": "No title"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    # -- update --

    def test_update_task_partial(self):
        task = Task.objects.create(title="Before")
        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"title": "After"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "After")
        self.assertEqual(Task.objects.get().title, "After")

    def test_update_task_full(self):
        task = Task.objects.create(title="Old", status=Task.Status.TODO)
        response = self.client.put(
            f"/api/tasks/{task.id}/",
            {
                "title": "Updated",
                "description": "Now detailed",
                "status": Task.Status.DONE,
                "due_date": "2026-12-31",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Task.Status.DONE)

    # -- delete --

    def test_delete_task(self):
        task = Task.objects.create(title="To remove")
        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Task.objects.count(), 0)

    # -- negative --

    def test_invalid_status_is_rejected(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": "Bad task", "status": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_with_null_title_rejected(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": None},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    # -- priority --

    def test_priority_default_is_medium(self):
        task = Task.objects.create(title="No priority")
        self.assertEqual(task.priority, Task.Priority.MEDIUM)

    def test_create_task_with_priority(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": "Urgent", "priority": "high"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(pk=response.data["id"])
        self.assertEqual(task.priority, Task.Priority.HIGH)

    def test_invalid_priority_is_rejected(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": "Bad priority", "priority": "critical"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_api_response_includes_priority(self):
        Task.objects.create(title="Check priority field", priority="low")
        response = self.client.get("/api/tasks/")
        self.assertIn("priority", response.data[0])
        self.assertEqual(response.data[0]["priority"], "low")
