
FROM node:18-alpine AS build
WORKDIR /usr/src/app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build
FROM node:18-alpine
WORKDIR /usr/src/app
RUN npm install -g serve
COPY --from=build /usr/src/app/dist ./dist
EXPOSE 3000
CMD ["serve","-s","dist","-l","3000"]
