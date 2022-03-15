# NFT Scanner

SaaS B2C\B2B сервис анализа NFT работ на предмет уникальности, степени похожести на чужие работы, проиндексированные в базе данных, анализ на плагиат и выдачу чужих работ за свои. (MVP проекта сделан в рамках хакатона Definition Насkathon в треке Rarible в команде SecurityBand). В проекте использовались алгоритмы кластеризации, нечетких хэшей (ssdeep), perceptual hash, avarage hash (MeanHash). 

SaaS B2C\B2B service for analyzing NFT works for uniqueness, degree of similarity to other works indexed in the database, analysis for plagiarism and passing off other works as your own. (The MVP of the project was done as part of the Definition Hackathon in the Rarible track of the SecurityBand team). The project used algorithms of clustering, fuzzy hash (ssdeep), perceptual hash, avarage hash (MeanHash). 

Translated with www.DeepL.com/Translator (free version)

### Project presentation \ Презентация проекта: https://cloud.mail.ru/public/qsDm/wm1BYYWdu. 
### Demo project \ Демо проекта: https://youtu.be/EnmbVleOJwQ

### Project run
```vim
docker build -t web-image .back
docker-compose up 
```

### Project update
```vim
docker-compose up -d --build
docker-compose down
```

### Run script
```vim
docker-compose exec web {script} 
```

### Swarm
```vim
docker swarm init --advertise-addr 127.0.0.1:2377
docker stack deploy -c docker-compose.yml  proj
```  
### Remove swarm 
```vim
docker stack rm proj
docker swarm leave --force
```
