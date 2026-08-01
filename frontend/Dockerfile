FROM --platform=$BUILDPLATFORM node:20-slim

WORKDIR /app

# Install deps first for layer caching.
COPY package.json ./
RUN npm install

# Source is bind-mounted in compose for live reload; copy for standalone build.
COPY . .

EXPOSE 5273

CMD ["npm", "run", "dev"]