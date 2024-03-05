FROM python:3.11.4
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y libgl1-mesa-glx

ENV TIME_ZONE Asia/Shanghai

RUN echo "${TIME_ZONE}" > /etc/timezone
RUN ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime

WORKDIR /logs
WORKDIR /projects

COPY . .

# RUN pip --no-cache-dir install  -i ${PIPURL} --upgrade pip
# RUN pip --no-cache-dir install  -i ${PIPURL} -r requirements.txt
RUN pip --no-cache-dir install --upgrade pip
RUN pip --no-cache-dir install -r requirements.txt

RUN chmod +x run.sh
CMD ./run.sh
# CMD tail -f /dev/null
