FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

# Install build dependencies and tools first
RUN apk add --no-cache python3 make g++ && npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 