# -*- coding: utf-8 -*-

"""
@author:  CongZheng
 
@Created on: 2021/6/3 003 0:30
@Remark: 角色管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Acars 
from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse, DetailResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator
from dvadmin.utils.viewset import CustomModelViewSet


class AcarsSerializer(CustomModelSerializer):
    """
    参数-序列化器
    """

    class Meta:
        model = Acars
        fields = "__all__"


class AcarsCreateUpdateSerializer(CustomModelSerializer):
    def validate(self, attrs: dict):
        return super().validate(attrs)

    class Meta:
        model = Acars
        fields = "__all__"

class AcarsViewSet(CustomModelViewSet, FastCrudMixin, FieldPermissionMixin):
    """
    参数管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Acars.objects.all()  # 这里定义的 queryset 将用于所有 CRUD 操作
    serializer_class = AcarsSerializer
    create_serializer_class = AcarsCreateUpdateSerializer
    update_serializer_class = AcarsCreateUpdateSerializer
    search_fields = ['name']  # 确保匹配模型中的字段名称

    def get_queryset(self):
        """
        根据请求中的 project_id 和 name 过滤 queryset
        """
        project_id = self.request.query_params.get('project_id')  # 获取项目ID参数
        name = self.request.query_params.get('name')  # 获取名称参数

        queryset = Acars.objects.all()  # 默认的 queryset

        # 根据 project_id 进行过滤
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # 根据 name 进行过滤
        if name:
            queryset = queryset.filter(name__icontains=name)  # icontains 用于模糊匹配

        return queryset  # 返回最终的 queryset

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