# astrocytes
## Components

* **Docker**: Eina per desplegar contenidors, que serveixen per virtualitzar una màquina pre-configurada (en aquest cas un sistema Ubuntu amb la instalacio de ROS).  
* **ROS**: Llibreria per controlar el robot. També inclou serveis per comunicar-s'hi desde fora (rosbridge).  
* **Epiplanner**: Aplicació en Python que es comunica amb el ROS per controlar el robot.  
* **Unity**: Representa el robot.
* A més fem serir el **conda** per instal·lar totes les llibreries de Python en un "entorn virtual", de manera que podem tenir una instal·lació compacta que podem esborrar facilment i ens estalviem possibles conflictes amb les llibraries que tenim instal·lades a la nostra màquina.   

## Arquitectura
* A la Maquina Local: Unity i Epiplanner.  
* A la Maquina Virtual (Docker): Instalació de Ros.  
* Flux de missatges: Epipplaner &rlarr; ROS &rlarr; Unity

## Desplegament
* ROS
  1. La primera vegada cal crear la imatge del Docker a partir del Dockerfile (S'ha d'executar desde sobre de les carpetes ros i docker.):  
      `docker build . -f docker/Dockerfile -t 2021ct`
  2. Podem veure quines imatges tenim creades:  
      `docker images`
  3. Per executar una instància d'aquesta màquina:  
      `docker run -it --rm -p 10000:10000 -p 5005:5005 -p 9090:9090 2021ct /bin/bash`
  4. Un cop dins la màquina, cambiar permisos del servei i llançar el controlador del robot:  
      `chmod u+x src/niryo_moveit/scripts/server_endpoint.py`  
      `roslaunch niryo_moveit part_3.launch`
  5. Obrim una nova terminal i mirem el nom o id del contenidor docker per obrir una nova conexio al docker:  
    `docker ps`  
    `docker exec -it ID-HERE /bin/bash`
  6. Executar el rosbridge:  
     `source devel/setup.bash`  
    `roslaunch rosbridge_server rosbridge_websocket.launch`

      
* Unity
    1. Importar/Obrir el projecte.
* Epiplanner
    1. La primera vegada cal crear l'entorn de Python:  
      `conda env create -f environment.yaml`
    2. Potser cal iniciar el conda, diferent depenent del sistema operatiu:  
      `conda init SHELL` (SHELL pot ser bash, zsh..) o potser n'hi ha prou amb `conda init`
    3. Activar l'entorn.
        `conda activate epi` (epi es el nom de l'entorn al fitxer environment.yaml)
    4. Executar l'aplicació
        `python main.py`
     
