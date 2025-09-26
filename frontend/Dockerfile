FROM node:22-alpine
WORKDIR /app

# 先装依赖（利用缓存）
COPY package*.json ./
RUN npm install

# 把源码复制进容器（第一次构建要有，不然 npm run dev 找不到文件）
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
