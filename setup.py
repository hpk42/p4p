#! /usr/bin/env python

import os, sys
from setuptools import setup, find_packages

if __name__ == "__main__":
    here = os.path.abspath(".")
    README = open(os.path.join(here, 'README.rst')).read()

    install_requires = ["webob"],
    if sys.version_info < (2,7):
        install_requires.append("argparse>=1.2.1")

    setup(
      name="friendsecure",
      description="lookup service for p2p messenger",
      long_description=README,
      version='0.1',
      maintainer="Holger Krekel",
      maintainer_email="holger@merlinux.eu",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      license="MIT",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ] + [
            ("Programming Language :: Python :: %s" % x) for x in
                "2.7 3.3".split()],
      install_requires=install_requires,
      entry_points = {
        'console_scripts':
                    ["friend_lookup_server = friend_lookup_server:main"],
      })

