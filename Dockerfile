FROM docker.an.local/base/python


#RUN apt-get update -qq && apt-get install -y vim
RUN pip install ansible==1.9.3

# Install docker client for running docker commands
RUN curl -sSL https://get.docker.com/ | sh
RUN wget -qO- https://get.docker.com/ | sed 's/lxc-docker/lxc-docker-1.6.2/' | sh

RUN mkdir /etc/ansible

COPY ansible.cfg /etc/ansible/
COPY app /app
COPY resolve.conf /etc/

EXPOSE 8888

WORKDIR /root

CMD ["python", "/app/dsh.py"]

WORKDIR /app
