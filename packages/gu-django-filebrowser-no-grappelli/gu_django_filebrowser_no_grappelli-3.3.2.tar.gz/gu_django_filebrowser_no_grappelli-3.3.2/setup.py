from setuptools import setup, find_packages

setup(
    name='gu-django-filebrowser-no-grappelli',
    version='3.3.2',
    description='Media-Management with the Django Admin-Interface. Without django-grappelli requirement.',
    author='Patrick Kranzlmueller',
    author_email='patrick@vonautomatisch.at',
    url='https://github.com/hu-django/filebrowser-no-grappelli',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ]
)
