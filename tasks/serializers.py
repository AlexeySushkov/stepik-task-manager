from rest_framework import serializers
from tasks.models import Task
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "due_date", "created_at"]
        read_only_fields = ["id", "created_at"]
