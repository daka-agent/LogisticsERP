# 前端 Dockerfile - 使用 Nginx 托管静态文件

# 第一阶段：构建
FROM node:24-alpine as build-stage

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 第二阶段：生产环境
FROM nginx:stable-alpine as production-stage

# 复制自定义 Nginx 配置
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
