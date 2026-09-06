FROM node:22-alpine AS build

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .
RUN npx tsc --noEmit \
    && node --experimental-strip-types --test src/components/studyText.test.mjs src/composables/tutorArchive.test.mjs \
    && npm run build

FROM nginx:stable-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
