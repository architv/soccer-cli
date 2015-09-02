from setuptools import setup

setup(name="football-scores",
      version="0.3",
      description="league standings and live scores for world football",
      author="Archit Verma",
      license="MIT",
      classifiers=["Development Status :: 3 - Alpha",  # 4: beta, 5: stable
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License"],
      keywords="soccer football espn scores live tool cli",
      author_email="architv07@gmail.com",
      url="https://github.com/architv/soccer-cli",
      install_requires=["click==5.0", "requests==2.7.0"],
      package_data={"football": ["clubs.json"]},
      entry_points={"console_scripts": ["football = football:main"]})
