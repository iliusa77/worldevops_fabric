"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup_nginx

"""
from fabric.contrib.files import upload_template
from unipath import Path
from fabric.colors import red
import fabtools
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'gitlab'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': 'git',
    'pass': genpass(),
    'port': 3306,
    'root': genpass()
}
env.local_root = Path(__file__).ancestor(2)


def install_ruby():
    sudo("apt-get -y remove ruby")
    run('rm -rf /tmp/ruby')
    run("mkdir /tmp/ruby")
    with cd("/tmp/ruby"):
        run("wget http://ftp.ruby-lang.org/pub/ruby/2.1/ruby-2.1.2.tar.gz")
        run("tar xvzf ruby-2.1.2.tar.gz")
        with cd("ruby-2.1.2"):
            run("./configure --disable-install-rdoc --prefix=/usr/local")
            run("make")
            sudo("make install")


def install_gitlab():
    with cd("/home/git"):
        sudo("sudo -u git -H git clone https://gitlab.com/gitlab-org/gitlab-ce.git -b 6-9-stable gitlab")
        with cd("gitlab"):
            source = Path(env.local_root, 'gitlab', 'gitlab.yml')
            destination = Path("config", "gitlab.yml")
            upload_template(
                filename=source,
                destination=destination,
                context={'domain': env.domain},
                use_sudo=True,
            )
            sudo("chown -R git {log,tmp}")
            sudo("chmod -R u+rwX {log,tmp,tmp/pids,tmp/sockets,public/uploads}")
            sudo("sudo -u git -H mkdir /home/git/gitlab-satellites")
            sudo("chmod u+rwx,g+rx,o-rwx /home/git/gitlab-satellites")
            sudo("sudo -u git -H cp config/unicorn.rb.example config/unicorn.rb")
            sudo("sudo -u git -H cp config/initializers/rack_attack.rb.example config/initializers/rack_attack.rb")
            source = Path(env.local_root, "gitlab", "database.yml")
            destination = Path("config", "database.yml")
            upload_template(
                filename=source,
                destination=destination,
                context={'db_name': env.db['name']},
                use_sudo=True,
            )
            sudo("gem install bundler")
            sudo("sudo -u git -H bundle install --deployment --without development test mysql aws")
            sudo("sudo -u git -H bundle exec rake gitlab:shell:install[v1.9.4] REDIS_URL=redis://localhost:6379 RAILS_ENV=production")
            sudo("sudo -u git -H bundle exec rake gitlab:setup RAILS_ENV=production")
            sudo("cp lib/support/init.d/gitlab /etc/init.d/gitlab")
            sudo("update-rc.d gitlab defaults 21")
            sudo("cp lib/support/logrotate/gitlab /etc/logrotate.d/gitlab")
            sudo("sudo -u git -H bundle exec rake gitlab:env:info RAILS_ENV=production")
            sudo("sudo -u git -H bundle exec rake assets:precompile RAILS_ENV=production")
            sudo("sudo -u git -H git config --global user.name \"GitLab\"")
            sudo("sudo -u git -H git config --global user.email \"gitlab@%s\"" % env.domain)
            sudo("sudo -u git -H git config --global core.autocrlf input")
            fabtools.service.start("gitlab")


def install_nginx():
    fabtools.require.nginx.server()
    source = Path(env.local_root, "gitlab", "gitlab")
    destination = Path("/", "etc", "nginx", "sites-available", "gitlab")
    upload_template(
        filename=source,
        destination=destination,
        context={"port": 80, "hostname": env.domain},
        use_sudo=True
    )
    fabtools.require.nginx.disable("default")
    sudo("ln -s /etc/nginx/sites-available/gitlab /etc/nginx/sites-enabled/gitlab")
    fabtools.service.restart("nginx")


def install_postgresql():
    fabtools.require.deb.packages(["postgresql-client", " libpq-dev"])
    fabtools.require.postgres.server()
    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
    fabtools.require.service.started('postgresql')


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Gitlab is successfully installed, visit http://%s") % env.domain)
    print(red("lodin - admin@local.host"))
    print(red("password - 5iveL!fe"))


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    with settings(abort_exception=FabricException):
            try:
                sudo("adduser --disabled-login --gecos 'GitLab' git")
            except FabricException:
                pass

    fabtools.require.deb.packages([
        "build-essential", "cmake", "zlib1g-dev", "libyaml-dev", "libssl-dev", "libgdbm-dev", "libreadline-dev",
        "libncurses5-dev", "libffi-dev", "curl", "openssh-server", "redis-server", "checkinstall", "libxml2-dev",
        "libxslt-dev", "libcurl4-openssl-dev", "libicu-dev", "logrotate", "git"
    ])
    fabtools.require.postfix.server('127.0.0.1')
    install_ruby()
    install_postgresql()
    install_gitlab()
    install_nginx()
    report()
