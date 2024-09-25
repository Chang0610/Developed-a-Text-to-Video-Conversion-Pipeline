FROM pytorch/pytorch:1.13.0-cuda11.6-cudnn8-runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         ca-certificates \
         libboost-all-dev \
         libjpeg-dev \
         libpng-dev \
         python3-setuptools \
         libgl1-mesa-glx libsm6 libxrender1 libxext-dev \
         nginx libgl1 && \
     rm -rf /var/lib/apt/lists/*

RUN conda install tornado=5.0.2 ply=3.11 
RUN pip install opencv-contrib-python==4.7.0.72 opencv-python==4.7.0.72 tqdm==4.45.0 \
librosa numba==0.56.4 numpy==1.23.5 validators oss2

COPY app/ /home/app/
COPY *.py /home/app/
COPY *.conf /etc/nginx/ 

RUN rm -fr /usr/bin/python*

CMD  ["/opt/conda/bin/python","/home/app/webs.py"]
WORKDIR /home/app

####
ARG  USER=docker
ARG  GROUP=docker
ARG  UID
ARG  GID
## must use ; here to ignore user exist status code
RUN  [ ${GID} -gt 0 ] && groupadd -f -g ${GID} ${GROUP}; \
     [ ${UID} -gt 0 ] && useradd -d /home -M -g ${GID} -K UID_MAX=${UID} -K UID_MIN=${UID} ${USER}; \
     chown -R ${UID}:${GID} /home && \
     touch /var/run/nginx.pid && \
     mkdir -p /var/log/nginx /var/lib/nginx && \
     chown ${UID}:${GID} $(find /home -maxdepth 2 -type d -print) /var/run/nginx.pid && \
     chown -R ${UID}:${GID} /var/log/nginx /var/lib/nginx
USER ${UID}
####
