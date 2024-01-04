FROM tls-baseimagedebian


# RUN cat /etc/ssl/cert-data/tls-server.com.key >> /etc/ssl/private/pure-ftpd.pem
# RUN cat /etc/ssl/cert-data/tls-server.com-chain.crt >> /etc/ssl/private/pure-ftpd.pem
# RUN apk add gnutls-dev wxgtk-dev pugixml-dev libexecinfo-dev libfilezilla-dev
RUN apt-get install -y gnutls-dev libwxgtk3.2-dev libpugixml-dev xz-utils
RUN apt-get install -y gettext
ARG LIBVERSION=0.45.0
WORKDIR /build
RUN wget https://download.filezilla-project.org/libfilezilla/libfilezilla-${LIBVERSION}.tar.xz
RUN tar -xvf libfilezilla-${LIBVERSION}.tar.xz
WORKDIR /build/libfilezilla-${LIBVERSION}
RUN ./configure --prefix=/usr
RUN make -j16
RUN make install
RUN mv lib/.libs/libfilezilla.a /usr/lib/

ARG VERSION=1.8.0
WORKDIR /build
RUN wget https://download.filezilla-project.org/server/FileZilla_Server_1.8.0_src.tar.xz
RUN tar -xvf FileZilla_Server_${VERSION}_src.tar.xz
WORKDIR /build/filezilla-server-${VERSION}
RUN ./configure --prefix=/usr
RUN make -j16
RUN mv src/server/filezilla-server /bin/

RUN echo root:root | chpasswd

CMD ["filezilla-server"]
