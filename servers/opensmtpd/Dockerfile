FROM tls-baseimage-archlinux
# ARG DEBIAN_FRONTEND=noninteractive
# RUN apt-get update && apt-get install -yq opensmtpd

RUN pacman -S --noconfirm opensmtpd

ADD smtpd.conf /etc/smtpd/smtpd.conf
# RUN chown opensmtpd:opensmtpd /etc/ssl/cert-data/*
RUN chmod 600 /etc/ssl/cert-data/* && mkdir /etc/mail && touch /etc/mail/secrets
CMD [ "smtpd", "-d" ]