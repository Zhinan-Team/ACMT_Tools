# 使用 Nginx 作为基础镜像
FROM nginx:alpine

# 从构建上下文复制 dist 文件夹到 Nginx 的 html 目录
COPY ./dist /usr/share/nginx/html

# 暴露 Nginx 的端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]