from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dvadmin.system.models import RuletoTask

from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse, DetailResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator
from dvadmin.utils.viewset import CustomModelViewSet

class RuletoTaskSerializer(CustomModelSerializer):
    class Meta:
        model = RuletoTask
        fields = "__all__"

class RuletoTaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuletoTask
        fields = "__all__"
        read_only_fields = ["dept_belong_id"]

class RuletoTaskViewSet(CustomModelViewSet, FastCrudMixin, FieldPermissionMixin):
    queryset = RuletoTask.objects.all()
    serializer_class = RuletoTaskSerializer
    create_serializer_class = RuletoTaskCreateUpdateSerializer
    update_serializer_class = RuletoTaskCreateUpdateSerializer
    search_fields = ['name']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def task_change(self, request):
        prename = request.query_params.get('prename')
        taskname = request.query_params.get('taskname')

        if not prename or not taskname:
            return Response({"message": "Missing parameters"}, status=400)

        # 查找所有相关的规则
        rules = RuletoTask.objects.all()
        
        for rule in rules:
            # 使用列表解析更新任务名
            updated_tasks = [taskname if task == prename else task for task in rule.taskname]
            # 更新并保存
            rule.taskname = updated_tasks
            rule.save()

        return Response({"message": "新记录更新成功哈哈"}, status=200)