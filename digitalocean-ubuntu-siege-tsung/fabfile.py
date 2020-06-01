from fabtools import *
from fabric.api import run, env, sudo, cd, put

def install_siege():
    sudo("apt-get update && apt-get install siege -y")

def install_tsung():
    require.deb.packages([
        'erlang', 'gnuplot-nox', 'libtemplate-perl',
        'libhtml-template-perl', 'libhtml-template-expr-perl'
    ])
    fabtools.require.nginx.server()
    with cd('/usr/src'):
        sudo('wget http://tsung.erlang-projects.org/dist/tsung-1.6.0.tar.gz')
        sudo('tar -xvf tsung-1.6.0.tar.gz')
        with cd('/usr/src/tsung-1.6.0'):
            sudo('./configure && make && make install')
    sudo('mkdir ~/.tsung && cp /usr/lib/tsung/bin/tsung_stats.pl ~/')
    put('./tsung.xml', '~/.tsung/', use_sudo=True)

def setup():
    install_siege()
    install_tsung()
