FROM node:lts-alpine as build-stage

WORKDIR /build

COPY package*.json ./

RUN npm install 

COPY . .

RUN npm run build:prod_docker

# production stage
FROM nginx:alpine as production-stage
WORKDIR /app
COPY --from=build-stage /build/dist /usr/share/nginx/html
EXPOSE 3000
# CMD ["npm", "start"]


# docker build . -t test-image:latest  

# docker images

# docker run -d -p 3000:80 --rm  --name test-container test-image:latest