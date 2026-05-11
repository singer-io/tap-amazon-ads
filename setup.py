

from setuptools import setup, find_packages


setup(name="tap-amazon-ads",
      version="1.0.1",
      description="Singer.io tap for extracting data from Amazon_Ads API",
      author="Stitch",
      url="http://singer.io",
      classifiers=["Programming Language :: Python :: 3 :: Only"],
      py_modules=["tap_amazon_ads"],
      install_requires=[
        "singer-python==6.8.0",
        "requests==2.33.1",
        "backoff==2.2.1"
      ],
      extras_require={"dev": ["pylint", "ipdb", "pytest"]},
      entry_points="""
          [console_scripts]
          tap-amazon-ads=tap_amazon_ads:main
      """,
      packages=find_packages(),
      package_data = {
          "tap_amazon_ads": ["schemas/*.json"],
      },
      include_package_data=True,
)
