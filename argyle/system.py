from fabric.api import put, sudo, task, env


def _read_lines_from_file(file_name):
    with open(file_name) as f:
        packages = f.readlines()
    return map(lambda x: x.strip('\n\r'), packages)


@task
def install_packages(*packages):
    """Install apt packages from a list."""

    sudo(u"apt-get install -y %s" % u" ".join(packages))


@task
def install_packages_from_file(file_name):
    """Install apt packages from a file list."""

    install_packages(*_read_lines_from_file(file_name))


@task
def update_apt_sources():
    """Update apt source."""

    sudo(u"apt-get update")


@task
def upgrade_apt_packages():
    """Safe upgrade of all packages."""

    update_apt_sources()
    sudo(u"apt-get upgrade -y")


@task
def add_ppa(name):
    """Add personal package archive."""

    sudo(u"add-apt-repository %s" % name)
    update_apt_sources()


@task
def add_ppas_from_file(file_name):
    """Add personal package archive from a file list."""

    for ppa in _read_lines_from_file(file_name):
        add_ppa(ppa)


@task
def create_user(name, groups=None, key_file=None):
    """Create a user. Adds a key file to authorized_keys if given."""

    groups = groups and u'-G %s' % u','.join(groups) or ''
    sudo(u"useradd -m %s -s /bin/bash %s" % (groups, name))
    sudo(u"passwd -d %s" % name)
    if key_file:
        sudo(u"mkdir -p /home/%s/.ssh" % name)
        put(key_file, u"/home/%s/.ssh/authorized_keys" % name, use_sudo=True)
        sudo(u"chown -R %(name)s /home/%(name)s/.ssh" % {'name': name})


@task
def service_command(name, command):
    """Run an init.d command."""

    service_command_template = getattr(env, 'ARGYLE_SERVICE_COMMAND_TEMPLATE',
                                       u'/etc/init.d/%(name)s %(command)s')
    sudo(service_command_template % {'name': name,
                                     'command': command})


@task
def start_service(name):
    """Start an init.d service."""

    service_command(name, u"start")


@task
def stop_service(name):
    """Stop an init.d service."""

    service_command(name, u"stop")


@task
def restart_service(name):
    """Restart an init.d service."""

    service_command(name, u"restart")
