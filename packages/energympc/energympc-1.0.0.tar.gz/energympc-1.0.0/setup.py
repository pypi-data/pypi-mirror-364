from setuptools import setup, find_packages

setup(
    name="energympc",  # переименовать
    version="1.0.0",  # Версия пакета
    packages=find_packages(),  # Автоматическое нахождение всех пакетов
    install_requires=["pyomo", "pandas", "numpy", "typing", "matplotlib"],  # Зависимости (если есть)
    include_package_data=True,
    author="imby",  # Ваше имя
    author_email="",  # Ваш email
    description="",  # Краткое описание
    long_description=open('README.md').read(),  # Долгое описание из README
    long_description_content_type='text/markdown',
    url="",  # Ссылка на репозиторий (не обязательно)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Лицензия
        "Operating System :: OS Independent",  # Операционная система
    ],
)