# FROM node:22-alpine
# WORKDIR /app

# # 先装依赖（利用缓存）
# COPY package*.json ./
# RUN npm install

# # 把源码复制进容器（第一次构建要有，不然 npm run dev 找不到文件）
# COPY . .

# EXPOSE 3000
# CMD ["npm", "run", "dev"]


# ---------- 构建阶段 ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci                  # 更稳定的安装方式
COPY . .
RUN npm run build           # 先构建出 .next 等产物

# ---------- 运行阶段 ----------
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/next.config.* ./
COPY --from=build /app/package*.json ./
COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next

RUN npm ci --omit=dev       # 只装生产依赖
EXPOSE 3000
# 运行生产服务器
CMD ["npm","run","start"]
