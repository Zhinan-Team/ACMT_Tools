# -*- coding: utf-8 -*-

"""
@author:  CongZheng
 
@Created on: 2021/6/3 003 0:30
@Remark: 角色管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Rule

from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse, DetailResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.system.models import Role, Menu, MenuButton

class RuleSerializer(CustomModelSerializer):
    """
    参数-序列化器
    """

    class Meta:
        model = Rule
        fields = "__all__"
        #read_only_fields = ["id"]

class RuleCreateUpdateSerializer(serializers.ModelSerializer):

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
        model = Rule
        fields = "__all__"
        read_only_fields = ["dept_belong_id"]


class RuleViewSet(CustomModelViewSet, FastCrudMixin, FieldPermissionMixin):
    """
    参数管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    create_serializer_class = RuleCreateUpdateSerializer
    update_serializer_class = RuleCreateUpdateSerializer
    search_fields = ['name']


    def get_queryset(self):
        """
        根据请求中的project_id过滤 queryset
        """
        # project_id = self.request.query_params.get('project_id')  # 获取项目ID参数
        name = self.request.query_params.get('name')


        # if project_id:
        #     # 如果提供了project_id，使用该ID过滤
        #     return Rule.objects.filter(project_id=project_id)
        
        if name:
            return  Rule.objects.filter(name__icontains=name)

        
        # 默认情况下，返回所有参数
        return Rule.objects.all()  # 返回一个空的 QuerySet


