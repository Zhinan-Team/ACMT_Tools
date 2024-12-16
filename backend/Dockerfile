# 选择基础镜像
FROM python:3.12

# 设置环境变量
ENV PYTHONUNBUFFERED 1

# 创建和设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器
COPY . /app/

# # 进行数据迁移
# RUN python manage.py migrate

# 暴露运行端口
EXPOSE 8000

# Migrate Database
# CMD ["python", "manage.py", "migrate"]

# 启动服务器命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]