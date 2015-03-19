
from fabric.api import run
from fabric.colors import green,yellow
from fabric.tasks import Task

from umd.base.install.utils import yum


class Configure(Task):
    """
    Base class for configuring UMD products.
    """
    def run(self, *args, **kwargs):
        self.pre()

        self.post()

    def pre(self):
        pass

    def post(self):
        pass
