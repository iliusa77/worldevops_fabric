FROM ubuntu:14.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get -qq update
RUN apt-get install -y curl git

#installation and update NPM
RUN apt-get install -y npm
RUN npm cache clean -f
RUN npm install -g n
RUN cd `whereis npm | cut -c 6- | xargs readlink -f | sed 's/.\{18\}$//'`
RUN npm install npm@latest

#installation Nodejs 6.9
RUN curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
RUN apt-get install -y nodejs

#installation Gulp
RUN npm install gulp

VOLUME ["/path_to_project"]

#build application
ADD . /app
WORKDIR /app 
RUN npm cache clean
RUN npm install

EXPOSE 3000

CMD ["npm", "start"]
