FROM tls-baseimagedebian as tolerance_tester

RUN apt-get install -y telnet net-tools ncat nano xinetd jq
RUN mkdir /tester
COPY ./tolerance_test.py /tester
COPY ./entrypoint.sh /tester
COPY ./xinetd-openssl /etc/xinetd.d/xinetd-openssl

WORKDIR /tester
EXPOSE 9999
ENTRYPOINT [ "bash", "/tester/entrypoint.sh" ]
