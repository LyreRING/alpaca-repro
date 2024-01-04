FROM kibatic/proftpd

ADD proftpd.conf /etc/proftpd/proftpd.conf
ADD tls.conf /etc/proftpd/tls.conf
COPY tls-server.com.key /etc/ssl/cert-data/tls-server.com.key
COPY tls-server.com-chain.crt /etc/ssl/cert-data/tls-server.com-chain.crt

RUN chmod 700 /etc/proftpd/proftpd.conf /etc/proftpd/tls.conf
