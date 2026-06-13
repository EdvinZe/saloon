FROM node:22-slim AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

ARG VITE_API_BASE_URL
ARG VITE_STRIPE_PUBLISHABLE_KEY
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_STRIPE_PUBLISHABLE_KEY=${VITE_STRIPE_PUBLISHABLE_KEY}

COPY . .
RUN npm run build

FROM node:22-slim AS runtime

WORKDIR /app

RUN npm install -g serve@14.2.4

COPY --from=build /app/dist ./dist

EXPOSE 3000

CMD ["sh", "-c", "serve -s dist -l tcp://0.0.0.0:${PORT:-3000}"]
