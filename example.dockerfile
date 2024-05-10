FROM nvcr.io/nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git python3-pip cmake

RUN pip3 install torch torchvision

WORKDIR .
RUN pip3 install cssutils scikit-learn scikit-image svgwrite svgpathtools matplotlib numpy cmake

RUN git clone --recursive https://github.com/IzhanVarsky/diffvg  \
    && cd diffvg  \
    && RTX_3090=1 python3 ./setup.py install  \
    && cd ..  \
    && rm -rf diffvg