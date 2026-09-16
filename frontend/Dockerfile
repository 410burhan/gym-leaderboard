FROM node:20-slim AS build
WORKDIR /app

# Vite inlines VITE_* env vars into the JS bundle at BUILD time, not at container
# runtime - so they have to arrive as build args, not a runtime env_file like the
# backend uses. This is a real gotcha with static-site containers worth knowing.
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_API_URL
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
ENV VITE_API_URL=$VITE_API_URL

COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
