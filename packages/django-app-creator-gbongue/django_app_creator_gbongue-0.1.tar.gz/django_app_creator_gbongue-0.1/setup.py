from setuptools import setup, find_packages

setup(
    name="django-app-creator-gbongue",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'django-app-creator=creator.__main__:run',
        ],
    },
    description="Package pour créer une app Django réutilisable rapidement.",
    author="GBONGUÉ DAVID",
    author_email="davidmade92@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires='>=3.6',
)
