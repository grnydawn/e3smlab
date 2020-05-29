"e3smlab setup module."

def main():

    from setuptools import setup
    from e3smlab.main import E3SMlab as elab

    console_scripts = ["e3smlab=e3smlab.__main__:main"]
    install_requires = ["meteolab>=0.3.0", "gunzip>=0.1.10", "nmlread>=0.1.5",
                        "dict2json>=0.1.2", "uxml2dict>=0.2.2",
                        "langlab>=0.3.0", "sqlalchemy", "pymysql"]

    setup(
        name=elab._name_,
        version=elab._version_,
        description=elab._description_,
        long_description=elab._long_description_,
        author=elab._author_,
        author_email=elab._author_email_,
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
        ],
        keywords="e3smlab",
        packages=[ "e3smlab" ],
        include_package_data=True,
        install_requires=install_requires,
        entry_points={ "console_scripts": console_scripts,
            "microapp.projects": "e3smlab = e3smlab"},
        project_urls={
            "Bug Reports": "https://github.com/grnydawn/e3smlab/issues",
            "Source": "https://github.com/grnydawn/e3smlab",
        }
    )

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
