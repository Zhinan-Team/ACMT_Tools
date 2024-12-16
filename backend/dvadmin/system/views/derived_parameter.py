# -*- coding: utf-8 -*-

"""
@author:  CongZheng
 
@Created on: 2021/6/3 003 0:30
@Remark: 角色管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import DerivedParameter 
from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse, DetailResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator
from dvadmin.utils.viewset import CustomModelViewSet
from django.db.models import Count

class DerivedParameterSerializer(CustomModelSerializer):
    """
    参数-序列化器
    """

    class Meta:
        model = DerivedParameter
        fields = "__all__"


class DerivedParameterCreateUpdateSerializer(CustomModelSerializer):
    def validate(self, attrs: dict):
        return super().validate(attrs)

    class Meta:
        model = DerivedParameter
        fields = "__all__"
    

class DerivedParameterViewSet(CustomModelViewSet, FastCrudMixin, FieldPermissionMixin):
    """
    参数管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = DerivedParameter.objects.all()  # 这里定义的 queryset 将用于所有 CRUD 操作
    serializer_class = DerivedParameterSerializer
    create_serializer_class = DerivedParameterCreateUpdateSerializer
    update_serializer_class = DerivedParameterCreateUpdateSerializer
    search_fields = ['parameter_name']

    def get_queryset(self):
        """
        根据请求中的 project_id 过滤 queryset
        """
        project_id = self.request.query_params.get('project_id')  # 获取项目ID参数
        parameter_name = self.request.query_params.get('parameter_name')

        # if project_id:
        #     # 如果提供了 project_id，使用该 ID 过滤
        #     return DerivedParameter.objects.filter(project_id=project_id)
        
        if parameter_name:
            # 返回完整的 Parameter 对象，使用 `distinct()` 或 `filter`
            return DerivedParameter.objects.filter(parameter_name__icontains=parameter_name).distinct()[:500]

        # 默认情况下，返回所有参数
        return DerivedParameter.objects.all()  # 或返回 Parameter.objects.none() 具体视情况而定

    def list(self, request, *args, **kwargs):
        """
        覆盖 list 方法以添加自定义逻辑
        """
        queryset = self.get_queryset()
        
        # 使用分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        
        # 如果没有分页，则返回全部数据
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")