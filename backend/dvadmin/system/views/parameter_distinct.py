# -*- coding: utf-8 -*-

"""
@author: CongZheng

@Created on: 2021/6/3 003 0:30
@Remark: 参数管理
"""
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import ParameterDistinct, DerivedParameter
from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from django.db.models import Q

class ParameterDistinctSerializer(CustomModelSerializer):
    """
    参数-序列化器
    """
    class Meta:
        model = ParameterDistinct
        fields = "__all__"

class DerivedParameterSerializer(CustomModelSerializer):
    """
    参数-序列化器
    """
    class Meta:
        model = DerivedParameter
        fields = "__all__"

class ParameterDistinctCreateUpdateSerializer(CustomModelSerializer):
    class Meta:
        model = ParameterDistinct
        fields = "__all__"

class CombinedParameterSerializer(serializers.Serializer):
    """
    联合参数序列化器
    """
    parameter_name = serializers.CharField()
    # 这里可以根据具体需要添加 DerivedParameter 的字段
    additional_field = serializers.CharField(source='some_field_here')  # 替换为 DerivedParameter 中的实际字段

    class Meta:
        fields = ['parameter_name', 'additional_field']


class ParameterDistinctViewSet(CustomModelViewSet, FastCrudMixin, FieldPermissionMixin):
    """
    参数管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = ParameterDistinct.objects.all()  # 这里定义的 queryset 将用于所有 CRUD 操作
    serializer_class = ParameterDistinctSerializer
    create_serializer_class = ParameterDistinctCreateUpdateSerializer
    update_serializer_class = ParameterDistinctCreateUpdateSerializer
    search_fields = ['parameter_name']

    def get_queryset(self):
        """
        根据请求中的 project_id 过滤 queryset。
        """
        project_id = self.request.query_params.get('project_id')
        parameter_name = self.request.query_params.get('parameter_name')

        filter_conditions = Q()

        # 获取 ParameterDistinct 的结果
        if project_id:
            filter_conditions |= Q(project_id=project_id)
        if parameter_name:
            filter_conditions |= Q(parameter_name__icontains=parameter_name)

        queryset_distinct = ParameterDistinct.objects.filter(filter_conditions).distinct()

        # 获取 DerivedParameter 的结果
        filter_conditions_derived = Q()
        if project_id:
            filter_conditions_derived |= Q(project_id=project_id)
        if parameter_name:
            filter_conditions_derived |= Q(parameter_name__icontains=parameter_name)

        queryset_derived = DerivedParameter.objects.filter(filter_conditions_derived).distinct()

        # 合并查询结果
        return queryset_distinct, queryset_derived


    def list(self, request):
        """
        返回 ParameterDistinct 和 DerivedParameter 去重结果的并集
        """
        # 获取去重的查询结果
        queryset_distinct, queryset_derived = self.get_queryset()

        # 序列化 ParameterDistinct 结果
        serializer_param_distinct = ParameterDistinctSerializer(queryset_distinct, many=True)
        
        # 序列化 DerivedParameter 结果
        serializer_derived_param = DerivedParameterSerializer(queryset_derived, many=True)

        # 创建一个统一的对象数组
        combined_results = []

        # 将 ParameterDistinct 的结果添加到 combined_results
        combined_results.extend(serializer_param_distinct.data)

        # 将 DerivedParameter 的结果添加到 combined_results
        combined_results.extend(serializer_derived_param.data)

        return SuccessResponse(data=combined_results, msg="获取成功")


