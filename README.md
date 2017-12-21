### Deployment:

    docker-compose up db

then in other terminal:

    docker exec -i jwter_db_1 mysql -hlocalhost -ujwter -pjwter -Djwter <jwter.sql

where `jwter.sql` is a data stored with `mysqldump`. Then do `Ctrl+C` on `docker-compose up db` and run:

    docker-compose up
    
This will run FastCGI server on local port 9001. To run local webserver on `http://localhost:9000/` run:

    docker-compose up -f docker-compose.yml -f docker-compose.runserver.yml  up

### Development
If you are going to develop `jwter` it is useful to uncomment `- .:/app` line in `docker-compose.yml` to make your changes to source files to be reflected in docker container.

### Mapcache
If you deploy `jwter` from SQL backup, remember to remove content of `areas_mapcache` table if you starting with empty mapcache folder
