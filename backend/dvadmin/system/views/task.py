# -*- coding: utf-8 -*-

"""
@author:  CongZheng
 
@Created on: 2021/6/3 003 0:30
@Remark: 角色管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Task

from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse, DetailResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.system.models import Role, Menu, MenuButton

class TaskSerializer(CustomModelSerializer):
    """
    参数-序列化器
    """

    class Meta:
        model = Task
        fields = "__all__"
        #read_only_fields = ["id"]

class TaskCreateUpdateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        # Remove 'request' from the keyword arguments
        kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data.pop('dept_belong_id', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('dept_belong_id', None)
        return super().update(instance, validated_data)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["dept_belong_id"]


class TaskViewSet(CustomModelViewSet, FastCrudMixin, FieldPermissionMixin):
    """
    参数管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    create_serializer_class = TaskCreateUpdateSerializer
    update_serializer_class = TaskCreateUpdateSerializer
    search_fields = ['task_name']


    def get_queryset(self):
        queryset = Task.objects.all()  # 使用所有任务作为基础查询集

        task_name = self.request.query_params.get('task_name')

        # project_id = self.request.query_params.get('project_id')
        # if project_id:
        #     queryset = queryset.filter(project_id=project_id)

        if task_name:
            queryset = queryset.filter(task_type="Parameter Recording Task")
            queryset = queryset.filter(task_name__icontains=task_name)

        return queryset.distinct()