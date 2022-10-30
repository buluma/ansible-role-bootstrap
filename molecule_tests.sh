#!/bin/bash -eu

MOLECULE_DISTROS="centos7 centos8 ubuntu1604 ubuntu1804	ubuntu2004 ubuntu2104 ubuntu2204"

for MOLECULE_DISTRO in $MOLECULE_DISTROS; do
  echo "*** $MOLECULE_DISTRO"
  export MOLECULE_DISTRO
  if [ -f tox.ini ] ; then tox ; fi
  if [ ! -f tox.ini ] ; then molecule test ; fi
done
