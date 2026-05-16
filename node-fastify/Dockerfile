FROM node:20-bookworm-slim

WORKDIR /app

COPY package.json ./
RUN npm install

COPY server.js .

EXPOSE 3000

ENV UV_THREADPOOL_SIZE=1

CMD ["node", "server.js"]