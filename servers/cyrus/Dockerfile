FROM tls-baseimagedebian

RUN apt-get install -y cyrus-common cyrus-imapd cyrus-pop3d cyrus-admin sasl2-bin

# RUN echo "tls-server" >> /etc/hostname
# RUN echo "tls-server 127.0.0.1" >> /etc/hosts

ADD cyrus.conf /etc/cyrus.conf
ADD imapd.conf /etc/imapd.conf
RUN chown cyrus /etc/ssl/cert-data/tls-server.com-chain.crt && \
chown cyrus /etc/ssl/cert-data/tls-server.com.key

RUN echo "cyrus:123" | chpasswd
RUN echo START=yes >> /etc/default/saslauthd

ADD start.sh /root
RUN chmod +x /root/start.sh

CMD [ "bash", "/root/start.sh"]
