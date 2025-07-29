from setuptools import setup, find_packages

setup(
    name="django-jazzmin-admin-rangefilter-jalali-plus",
    version="1.0.0",
    description="Jalali date support for Django Jazzmin admin with rangefilter",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sajjad Mousavi",
    author_email="Sajjadmoosavi90@gmail.com",
    url="https://github.com/sajjadmoosavi/django_jazzmin_admin_rangefilter_jalali_plus",
    packages=find_packages(include=["rangefilter2", "rangefilter2.*"]),
    include_package_data=True,
    install_requires=[
        "django>=4.0",
        "django-jalali-date>=2.0.0",
        "django-admin-rangefilter>=0.9.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
