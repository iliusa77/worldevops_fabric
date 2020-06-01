1. put files gulpfile.js and package.json in directory /path_to_project/app
2. start build docker container for application: 
docker build -t app_name .
3. run docker container:
docker run -d -p 3000:3000 app_name 
or
docker-compose up -d
4. open http://ip_container:3000
