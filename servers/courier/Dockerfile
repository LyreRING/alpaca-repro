FROM tls-baseimagedebian

# Avoid ERROR: invoke-rc.d: policy-rc.d denied execution of start.
#RUN echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d

# USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y courier-imap courier-pop courier-authlib-mysql courier-mta gamin rsyslog rpcbind telnet net-tools

RUN useradd bob -d /home/bob
RUN echo bob:12345 | chpasswd
RUN mkdir /home/bob/
RUN maildirmake /home/bob/Maildir
ADD mail.eml /home/bob/Maildir/cur/1602771604.M265899P242V0000000000000036I00000000001A0657_0.f178b3e21560,S=851^%2,S
RUN chmod -R 777 /home/bob/Maildir
RUN chown -R bob:bob /home/bob

RUN cat /etc/ssl/cert-data/tls-server.com.key /etc/ssl/cert-data/tls-server.com-chain.crt > /etc/courier/pop3d.pem && \
chmod 700 /etc/courier/pop3d.pem && \
chown courier /etc/courier/pop3d.pem && \
cp /etc/courier/pop3d.pem /etc/courier/imapd.pem

RUN cp /etc/ssl/cert-data/tls-server.com-chain.crt /etc/courier/imapd.cert
RUN cp /etc/ssl/cert-data/tls-server.com-chain.crt /etc/courier/pop3d.cert
RUN cp /etc/ssl/cert-data/tls-server.com.key /etc/courier/imapd.key
RUN cp /etc/ssl/cert-data/tls-server.com.key /etc/courier/pop3d.key

ADD start.sh /root/
# ADD imapd-ssl /etc/courier/
# RUN chmod +x /root/start.sh && mkdir -p /var/spool/courier

RUN chmod +x /root/start.sh
CMD ["/root/start.sh"]
