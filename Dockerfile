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

aes.decode(aes.asByte("0007D17B085C0DB78ED295719019052F2579208C6D01D321D08E15E2B17B7DA23501"))
