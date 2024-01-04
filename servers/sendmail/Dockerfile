FROM tls-baseimagedebian

RUN echo "deb http://ftp.debian.org/debian experimental main contrib non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y openssl sendmail
RUN apt-get update && apt-get install -y -t experimental sendmail sendmail-bin sendmail-base sendmail-cf

RUN echo "target.com" > /etc/hostname
RUN echo "include(\`/etc/mail/tls/starttls.m4')dnl" >> /etc/mail/sendmail.mc
RUN echo "include(\`/etc/mail/tls/starttls.m4')dnl" >> /etc/mail/submit.mc

RUN echo "define(\`confCACERT_PATH', \`/etc/ssl/cert-data/')dnl" >> /etc/mail/sendmail.mc
RUN echo "define(\`confSERVER_CERT', \`/etc/ssl/cert-data/tls-server.com-chain.crt')dnl" >> /etc/mail/sendmail.mc
RUN echo "define(\`confSERVER_KEY', \`/etc/ssl/cert-data/tls-server.com.key')dnl" >> /etc/mail/sendmail.mc
RUN echo "define(\`confCLIENT_CERT', \`/etc/ssl/cert-data/tls-server.com-chain.crt')dnl" >> /etc/mail/sendmail.mc
RUN echo "define(\`confCLIENT_KEY', \`/etc/ssl/cert-data/tls-server.com.key')dnl" >> /etc/mail/sendmail.mc
RUN echo "define(\`confLOG_LEVEL', \`14')" >> /etc/mail/sendmail.mc

RUN sed -i 's/127.0.0.1/0.0.0.0/' /etc/mail/sendmail.mc
RUN chown 600 /etc/ssl/cert-data

RUN apt-get update && apt-get install -y nano rsyslog telnet net-tools

ADD entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh
ENTRYPOINT /opt/entrypoint.sh
