from setuptools import setup

setup(name='intrinio',
      version='0.1',
      description='Unofficial Intrinio SDK',
      url='http://github.com/finnpy/intrinio',
      author='Tom Paoletti',
      author_email='zommaso@gmail.com',
      license='MIT',
      packages=['intrinio'],
      install_requires=[
          'requests',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
