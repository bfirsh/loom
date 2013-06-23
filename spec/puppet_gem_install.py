from pspec import describe
from loom.puppet import _gem_install


with describe('_gem_install'):
    def it_gem_install_no_version():
        assert 'gem install mygem --no-ri --no-rdoc' == _gem_install('mygem')

with describe('_gem_install'):
    def it_gem_install_version():
        assert 'gem install mygem -v 3.2.1 --no-ri --no-rdoc' == _gem_install('mygem', '3.2.1')
