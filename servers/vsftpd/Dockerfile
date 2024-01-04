FROM tls-baseimagedebian AS tls-vsftpd

RUN apt-get install -y vsftpd
RUN mkdir /vsftpd && echo root:root | chpasswd
COPY ./vsftpd.conf /etc/vsftpd.conf
# CMD [ "/usr/sbin/vsftpd" ]
COPY ./start.sh /root/start.sh
RUN echo root:root | chpasswd
CMD [ "bash", "/root/start.sh" ]
