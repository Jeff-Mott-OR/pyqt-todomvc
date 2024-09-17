# A PyQt cross-OS desktop app

I copied the [Common PyQt Widgets](https://github.com/pyqt/examples/blob/_/src/02%20PyQt%20Widgets) example program, but restructured the code to my taste.

The [Packaging & deployment](https://github.com/pyqt/examples/tree/_/src/08%20PyQt6%20exe) example program steered me to the [fman build system](https://build-system.fman.io/) (aka fbs) to make a standalone executable for each of the big three OSes. The paid version of fbs works with the latest Python and PyQt, but the free version is limited to older versions. I'm using the free version here, so I have to use Python3.6 instead of Python3.12, and PyQt5 instead of PyQt6.

## Usage

    $ fbs run

## Dependencies

Things you'll need to do first:

1. Get Python3.6. I used [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions.

2.

    $ python -m venv venv

This creates a "virtual environment". It's similar to site_modules from npm. It will locally contain any packages you install. [More.](https://docs.python.org/3/library/venv.html)

3.

    $ source venv/bin/activate

Execute shell commands for the virtual environment. It adds stuff to your PATH and whatnot.

4.

    $ (venv) pip install PyQt5 PyEventEmitter

[More.](https://riverbankcomputing.com/software/pyqt/intro)

5.

    $ (venv) pip install fbs

All done, ready to use.

## Reproducible builds with Vagrant

Build for other OSes by generating a VM from a vagrant configuration file. [More.](https://developer.hashicorp.com/vagrant/intro)

### Windows

    $ cd vagrant/windows-10
    $ vagrant up

If all goes well, your source directory will contain a Windows setup installer, at `<pyqt-todo>/target/MyFbsAppSetup.exe`.
