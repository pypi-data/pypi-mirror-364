from setuptools import setup, find_packages
long_description=open("README.md").read()
setup(
    name="django-barobill",  # 패키지 이름 (PyPI에 등록될 이름)
    version="0.1.3",  # 초기 버전
    packages=find_packages(exclude=["tests*", "docs*"]),  # 'django_barobill' 폴더 포함
    include_package_data=True,  # MANIFEST.in 파일에 포함된 파일도 추가
    license="MIT License",  # 라이선스
    description="A reusable Django app for integration with BaroBill services.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # README의 마크다운 형식 지원
    url="https://github.com/cuhong/django-barobill",  # 깃허브 등의 URL
    author="cuhong",
    author_email="hongcoilhouse@gmail.com",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.0",  # 해당 Django 버전
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",  # 최소 파이썬 버전
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",  # 지원 파이썬 버전
    install_requires=[
        "django>=4.0",  # Django 패키지 요구사항
        "requests==2.32.3",
        "zeep==4.3.1"
    ],
)
