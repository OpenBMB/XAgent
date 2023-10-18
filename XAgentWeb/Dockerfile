# FROM 基于node的版本镜像，并通过构建阶段命名，将有node环境的阶段命名为build-stage
FROM node:lts-alpine as build-stage
# 设置工作区为 /build 于系统文件隔离
WORKDIR /build
# copy package.json/package-lock.json 到容器 /build 目录
COPY package*.json ./
# 在容器中安装依赖
RUN npm install 
# 拷贝其他文件到容器 /build 目录，分两次拷贝是因为保持 node_modules 一致
COPY . .
# 打包
RUN npm run build:prod_docker

# production stage
FROM nginx:alpine as production-stage
WORKDIR /app
COPY --from=build-stage /build/dist /usr/share/nginx/html
EXPOSE 3000
# CMD ["npm", "start"]

# 创建镜像
# docker build . -t test-image:latest  
# 通过 docker images 命令查看所有镜像
# docker images

# 创建并启动container  映射端口  本地/linux 默认80   例 3000/80
# docker run -d -p 3000:80 --rm  --name test-container test-image:latest
# run：创建并运行 docker 容器
# -d： 后台运行容器
# 3000:80：将当前服务器的 80 端口（冒号前的 80），映射到容器的 80 端口（冒号后的 80）
# --name：给容器命名，便于之后定位容器
# test-image:latest：基于 test-image 最新版本的镜像创建容器



