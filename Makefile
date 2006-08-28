DESTDIR=
PREFIX=${DESTDIR}/usr
BINDIR=${PREFIX}/bin
LIBDIR=${PREFIX}/lib
PYDIR=${LIBDIR}/python2.4/site-packages
INSTALL_DIR=${PYDIR}/sfwg
CONFIG_DIR=${DESTDIR}/etc/sfwg

all:

install:
	install -d ${INSTALL_DIR}
	install -d ${BINDIR}
	install -m 755 src/*.py ${INSTALL_DIR}/
	ln -sf ${INSTALL_DIR}/sfwg.py ${BINDIR}/sfwg
	install -d ${CONFIG_DIR}
	install -b -S ".bak" -m 644 forwards.conf ${CONFIG_DIR}/
	install -b -S ".bak" -m 644 services.conf ${CONFIG_DIR}/

uninstall:
	rm -rf ${INSTALL_DIR}
	rm -f ${BINDIR}/sfwg

distclean: uninstall
	rm -rf ${CONFIG_DIR}

clean:
	rm -f src/*.pyc
	rm -f src/*.pyo
