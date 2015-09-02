from setuptools import setup

setup(name="football",
      version="0.3",
      description="league standings and live scores for world football",
      author="Archit Verma",
      license="MIT",
      classifiers=["Development Status :: 3 - Alpha",  # 4: beta, 5: stable
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License"],
      keywords="soccer football espn scores live tool cli",
      author_email="architv07@gmail.com",
      url="https://github.com/architv/soccer-cli",
      install_requires=["click", "requests"],
      package_data={"football": ["org.football-data.api.json"]},
      entry_points={"console_scripts": ["football = football:main"]})
