from setuptools import setup

setup(name='zefix_crawler',
      version='0.1.0',
      packages=['zefix_crawler'],
      entry_points={
          'console_scripts': [
              'my_project = zefix_crawler.__main__:main'
          ]
      },
)
