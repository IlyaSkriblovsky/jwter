Deployment:

    docker-compose up db

then in other terminal:

    docker exec -i jwter_db_1 mysql -hlocalhost -ujwter -pjwter -Djwter <jwter.sql

where `jwter.sql` is a data stored with `mysqldump`. Then do `Ctrl+C` on `docker-compose up db` and run:

    docker-compose up

**NOTE**: remove content of `areas_mapcache` table if you starting with empty mapcache folder
