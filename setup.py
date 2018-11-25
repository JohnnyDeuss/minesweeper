from setuptools import setup, find_packages


setup(name='minesweeper',
      version='1.0',
      description='Minesweeper game',
      author='Johnny Deuss',
      author_email='johnnydeuss@gmail.com',
      url='https://github.com/JohnnyDeuss/minesweeper',
      project_urls={'Source': 'https://github.com/JohnnyDeuss/minesweeper'},
      install_requires=['PyQt5==5.11.3'],
      packages=find_packages()
    )
