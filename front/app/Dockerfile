FROM node:16-alpine
WORKDIR /front_app


COPY . .
# RUN yarn add -D esbuild@0.13.4
RUN npm install

EXPOSE 5173
# ENV HOST=0.0.0.0

CMD ["npm", "run", "dev", "--", "--host"]