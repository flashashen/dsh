FROM docker.an.local/base/python-notebook


#RUN apt-get update -qq && apt-get install -y vim
RUN pip install ansible==1.9.3
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension

RUN echo 'invalidate cache'


# Install docker client for running docker commands
RUN curl -sSL https://get.docker.com/ | sh
RUN wget -qO- https://get.docker.com/ | sed 's/lxc-docker/lxc-docker-1.6.2/' | sh

RUN mkdir /etc/ansible

COPY ansible.cfg /etc/ansible/
COPY . /app
COPY resolve.conf /etc/

EXPOSE 8888

WORKDIR /root

CMD ["jupyter", "notebook", "--FileContentsManager.auto_save_as_py=False"]

WORKDIR /app

