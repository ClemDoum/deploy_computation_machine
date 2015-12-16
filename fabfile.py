from __future__ import with_statement

from fabric.api import *

import config

env.hosts = config.HOST
env.user = config.USER
env.key_filename = config.SSH_KEY_FILE


def setup():
    # Update
    sudo("apt-get update -y", shell=False)

    # Install compilers and dev tools
    sudo("apt-get install build-essential -y", shell=False)

    # Install git
    sudo("apt-get install git -y", shell=False)

    # Install python
    sudo("apt-get install build-essential autoconf libtool pkg-config "
         "python-opengl python-imaging python-pyrex python-pyside.qtopengl "
         "idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 "
         "libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus "
         "python-qt4 python-qt4-gl libgle3 python-dev -y", shell=False)
    # Install java
    sudo("apt-get install openjdk-7-jre -y", shell=False)
    sudo("apt-get install python-pip -y", shell=False)


def install_theano():
    # Bliding edge theano
    run("git clone git://github.com/Theano/Theano.git")
    with cd("theano"):
        run("python setup.py install")
    # Blas installation
    run("git clone git://github.com/xianyi/OpenBLAS")
    with("cd OpenBLAS"):
        run("make FC=gfortran")
        sudo("make PREFIX=/usr/local/ install", shell=False)
    # Theano flags
    run('echo -e "\n[global]\nfloatX = float32\n" '
        'openmp = True\n'
        '[blas]\n'
        'ldflags = -lopenblas\n'
        ' >> ~/.theanorc')
    # Set config.OMP_NUM_THREADS
    run('echo -e "\nexport config.OMP_NUM_THREADS=%s\n"'
        % config.OMP_NUM_THREADS)


def install_HDF5():
    sudo("apt-get install libhdf5-dev -y", shell=False)


def install_h5py():
    install_HDF5()
    sudo("pip install h5py", shell=False)


def install_keras():
    install_h5py()
    sudo("pip install git+git://github.com/Theano/Theano.git", shell=False)


def install_scipy():
    sudo("apt-get install libblas-dev liblapack-dev libatlas-base-dev "
         "gfortran -y", shell=False)
    # Install scipy
    sudo("pip install scipy", shell=False)
    # Install scipy common tools
    sudo("apt-get install libfreetype6-dev libpng12-dev -y", shell=False)


def install_xgboost():
    run("git clone https://github.com/dmlc/xgboost.git")
    with cd("xgboost"):
        sudo("make", shell=False)
        sudo("python setup install", shell=False)
    run("rm -rf xgboost")


def install_python_libs():
    # Cython, numpy, scipy first
    sudo("pip install cython", shell=False)
    sudo("pip install numpy", shell=False)
    install_scipy()
    sudo("apt-get install python-matplotlib -y", shell=False)
    # Python libs
    sudo("pip install -r %s/requirements.txt" % config.WORKING_DIR,
         shell=False)
    # Install theano
    install_theano()
    # Install keras
    install_keras()
    # Install xgboot
    install_xgboost()


def commit():
    local("git add -p && git commit")


def push():
    local("git push")


def generate_ssh_key():
    # Generating a public key
    run('ssh-keygen -t rsa -b 4096 -C "%s"' % config.GITHUB_EMAIL)


def deploy_code():
    with settings(warn_only=True):
        if run("ls %s" % config.WORKING_DIR).failed:
            if run("cat ~/.ssh/id_rsa.pub").failed:
                generate_ssh_key()
                raise ValueError(
                        "Please add the  ~/.ssh/id_rsa.pub  ssh key that has"
                        " been generated to Github")
            if run("git clone %s %s" % (config.GITHUB_REPO_URL,
                                        config.WORKING_DIR)).failed:
                raise ValueError("Add your ssh key to Github")
    with cd(config.WORKING_DIR):
        run("git pull")


def commit_push_and_deploy_code():
    commit()
    push()
    deploy_code()
