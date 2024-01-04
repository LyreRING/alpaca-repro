FROM tls-baseimagedebian
RUN apt-get update && apt-get install -y dovecot-imapd dovecot-pop3d
RUN cp /etc/ssl/cert-data/tls-server.com-chain.crt /etc/dovecot/private/dovecot.pem
RUN cp /etc/ssl/cert-data/tls-server.com.key /etc/dovecot/private/dovecot.key
RUN echo "ssl_min_protocol = TLSv1.2" >> /etc/dovecot/conf.d/10-ssl.conf
RUN useradd lyre && echo lyre:12345 | chpasswd && mkdir -p /home/lyre && chown lyre:lyre /home/lyre && echo root:root | chpasswd
CMD ["dovecot", "-F"]
