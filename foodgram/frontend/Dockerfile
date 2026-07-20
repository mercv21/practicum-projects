FROM node:21.7.1-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build

FROM alpine:3.18
WORKDIR /app
COPY --from=build /app/build /app/result_build
