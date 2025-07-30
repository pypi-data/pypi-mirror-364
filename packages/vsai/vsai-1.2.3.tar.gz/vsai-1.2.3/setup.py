import setuptools

setuptools.setup(
    name="vsai",
    version="1.2.3",
    packages=setuptools.find_packages(),
    url="https://github.com/Virtosync/vsai",
    author="Virtosync",
    license="Virto License",
    author_email="virtosync@gmail.com",
    description="A new AI assistant for your terminal",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "nltk",
        "textblob",
        "requests",
        "pyttsx3",
        "SpeechRecognition",
        "cryptography",
    ],
    entry_points={
        "console_scripts": [
            "vsai=vsai.bot:start"
        ]
    }
)