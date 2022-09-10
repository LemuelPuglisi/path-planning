import setuptools


setuptools.setup(name='path-planning',
                 version='0.0.0',
                 description='path-planning algorithms application and visualization',
                 long_description=open('README.md').read().strip(),
                 author='Lemuel Puglisi',
                 author_email='lemuelpuglisi001@gmail.com',
                 url='https://github.com/LemuelPuglisi/path-planning',
                 py_modules=['pathplanning'],
                  entry_points={
                     'console_scripts': [
                        'path-planning = pathplanning.cli:run_application', 
                     ]
                 },
                 install_requires=[
                    'numpy',
                    'PyQT5',
                    'networkx'
                 ],
                 license='MIT License',
                 zip_safe=False,
                 keywords='robotics, path planning',
                 classifiers=[
                    'Intended Audience :: Education',
                    'Topic :: Scientific/Engineering',
                    'License :: MIT License',
                    'Programming Language :: Python :: 3.9',
                ])