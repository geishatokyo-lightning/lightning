try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='lightning_core',
    version='0.5.0',
    description='swf to svg parser',
    author='Takashi Aoki, Masahiro Yamauchi, Ryoko Kato',
    author_email='info@geishatokyo.com',
    url='http://www.geishatokyo.com/',
    install_requires=[
      "lxml==2.3.1",
      "nose==1.1.2",
      "simplejson==2.2.1",
    ],
    test_suite='nose.collector',
    packages=['lightning_core'] + find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
)
