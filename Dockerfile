FROM balenalib/raspberrypi4-64-ubuntu-python:3.7.4

RUN apt-get update && \
  apt-get install -yq \
    git \
    build-essential \
    gcc-arm-linux-gnueabihf \
    libraspberrypi-bin \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/RPi-Distro/RTIMULib && \
  cd ./RTIMULib/Linux/python/ && \
  python setup.py build && \
  python setup.py install

COPY . .

# CMD ["python3", "camera_ioc.py"]
CMD ["python", "-c", "import time; time.sleep(10000000)"]




# docker run -d caproto-lesson-1
# docker exec -it b738 /bin/bash