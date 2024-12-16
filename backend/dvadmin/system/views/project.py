import os
import subprocess
import threading
import time
from django.http import FileResponse
from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Project
from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, ErrorResponse, SuccessResponse

# 用于存储任务状态
task_status = {}

class ProjectSerializer(CustomModelSerializer):
    """
    项目-序列化器
    """
    class Meta:
        model = Project
        fields = "__all__"


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = "__all__"


class ProjectViewSet(CustomModelViewSet, FastCrudMixin, FieldPermissionMixin):
    """
    项目管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    run_notebook: 运行 Jupyter Notebook
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    create_serializer_class = ProjectCreateUpdateSerializer
    update_serializer_class = ProjectCreateUpdateSerializer
    search_fields = ['name']

    def get_queryset(self):
        """
        根据请求中的 user_id 过滤 queryset
        """
        user_id = self.request.query_params.get('user_id')

        if user_id:
            return Project.objects.filter(user_id=user_id)
        
        return super().get_queryset()

    # @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    # def run_notebook(self, request):
    #     notebook_path = "/Users/congzheng/Desktop/ICD/ICDScript/script/icd3(Insert Json to 8294).ipynb"
        
    #     if not os.path.exists(notebook_path):
    #         return Response({"message": "Notebook 文件未找到", "path": notebook_path}, status=status.HTTP_404_NOT_FOUND)

    #     # 创建一个唯一的任务 ID
    #     task_id = str(os.urandom(16).hex())

    #     # 启动一个新的线程来执行 Notebook
    #     threading.Thread(target=self.execute_notebook, args=(notebook_path, task_id)).start()
        
    #     return SuccessResponse({"task_id": task_id, "status": "running"}, status=status.HTTP_200_OK)

    # def execute_notebook(self, notebook_path, task_id):
    #     task_status[task_id] = {"status": "running", "output": "", "progress": 0, "output_file": None}
        
    #     try:
    #         # 这里调用 nbconvert 执行 notebook 并导出结果
    #         result = subprocess.run(
    #             ['jupyter', 'nbconvert', '--to', 'notebook', '--execute', notebook_path],
    #             check=True,
    #             capture_output=True,
    #             text=True
    #         )
            
    #         # 假设 Jupyter notebook 执行后，下面是生成的输出文件路径
    #         output_file = "/Users/congzheng/Desktop/ICD/ICDScript/11145_update.json"  # 这里请根据实际生成路径修改
    #         task_status[task_id] = {
    #             "status": "completed",
    #             "output": result.stdout,
    #             "error": "",
    #             "output_file": output_file  # 保存输出文件路径
    #         }

    #     except subprocess.CalledProcessError as e:
    #         task_status[task_id] = {
    #             "status": "failed",
    #             "output": "",
    #             "error": str(e)
    #         }
    #     except Exception as e:
    #         task_status[task_id] = {
    #             "status": "failed",
    #             "output": "",
    #             "error": str(e)
    #         }

    # @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    # def check_status(self, request):
    #     task_id = self.request.query_params.get('task_id')
    #     status_info = task_status.get(task_id, None)

    #     if status_info:
    #         if status_info["status"] == "running":
    #             progress = status_info.get("progress", 0)  # 获取进度
    #             return SuccessResponse({"task_id": task_id, "status": "running", "progress": progress}, status=status.HTTP_200_OK)

    #         elif status_info["status"] == "completed":
    #             output_file = status_info.get("output_file")
    #             return SuccessResponse({"task_id": task_id, "status": "completed", "output_file": output_file}, status=status.HTTP_200_OK)

    #     else:
    #         return Response({"message": "无效的任务 ID"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def run_notebook(self, request):
        notebook_path = "/Users/congzheng/Desktop/ICD/ICDScript/script/icd3(Insert Json to 8294).ipynb"
        
        if not os.path.exists(notebook_path):
            return ErrorResponse({"message": "Notebook 文件未找到", "path": notebook_path}, status=status.HTTP_404_NOT_FOUND)

        # 创建一个唯一的任务 ID
        task_id = str(os.urandom(16).hex())
        
        # 记录任务开始时间
        start_time = time.time()

        # 启动一个新的线程来执行 Notebook
        threading.Thread(target=self.execute_notebook, args=(notebook_path, task_id, start_time)).start()

        return SuccessResponse({"task_id": task_id, "status": "running"}, status=status.HTTP_200_OK)

    def execute_notebook(self, notebook_path, task_id, start_time):
        task_status[task_id] = {"status": "running", "output": "", "start_time": start_time, "output_file": None}
        
        try:
            # 执行 Notebook
            result = subprocess.run(
                ['jupyter', 'nbconvert', '--to', 'notebook', '--execute', notebook_path],
                check=True,
                capture_output=True,
                text=True
            )
            
            output_file = "/Users/congzheng/Desktop/ICD/ICDScript/11145_update.json"  # 根据实际生成路径修改
            task_status[task_id] = {
                "status": "completed",
                "output": result.stdout,
                "error": "",
                "output_file": output_file
            }

        except subprocess.CalledProcessError as e:
            task_status[task_id] = {
                "status": "failed",
                "output": "",
                "error": str(e)
            }
        except Exception as e:
            task_status[task_id] = {
                "status": "failed",
                "output": "",
                "error": str(e)
            }

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def check_status(self, request):
        task_id = self.request.query_params.get('task_id')
        status_info = task_status.get(task_id, None)

        if status_info:
            if status_info["status"] == "running":
                current_time = time.time()
                run_time = current_time - status_info["start_time"]  # 计算已运行时间
                run_time_seconds = int(run_time)  # 将时间转换为秒
                return SuccessResponse({"task_id": task_id, "status": "running", "run_time": run_time_seconds}, status=status.HTTP_200_OK)

            elif status_info["status"] == "completed":
                output_file = status_info.get("output_file")
                return SuccessResponse({"task_id": task_id, "status": "completed", "output_file": output_file}, status=status.HTTP_200_OK)

        else:
            return ErrorResponse({"message": "无效的任务 ID"}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_file(self, request):
        file_name = self.request.query_params.get('file_name')
        file_path = os.path.join("/Users/congzheng/Desktop/ICD/ICDScript", file_name)  # 更新成实际的文件路径

        if os.path.exists(file_path):
            response = SuccessResponse(open(file_path, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
        else:
            return ErrorResponse({"message": "文件未找到"}, status=status.HTTP_404_NOT_FOUND)