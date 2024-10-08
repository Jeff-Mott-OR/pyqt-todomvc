# A PyQt TodoMVC cross-OS desktop app

In the spirit of [TodoMVC](https://todomvc.com/), I used [PyQt](https://riverbankcomputing.com/software/pyqt/intro) (Python + [Qt](https://doc.qt.io/qt-6/qt-intro.html)) to create a cross-OS desktop todo app. And I used the [fman build system](https://build-system.fman.io/) (aka fbs) to package the Python runtime and the Qt library binaries into a standalone executable and installer for each of the big three OSes.

| Mac  | Ubuntu | Windows |
| :--: | :----: | :-----: |
| ![Mac installer](https://raw.githubusercontent.com/Jeff-Mott-OR/pyqt-todomvc/refs/heads/assets/PyQtTodoMVCDmg.png) | ![Ubuntu installer](https://raw.githubusercontent.com/Jeff-Mott-OR/pyqt-todomvc/refs/heads/assets/PyQtTodoMVCDeb.png) | ![Windows installer](https://raw.githubusercontent.com/Jeff-Mott-OR/pyqt-todomvc/refs/heads/assets/PyQtTodoMVCSetup.png) |
| ![Mac app](https://raw.githubusercontent.com/Jeff-Mott-OR/pyqt-todomvc/refs/heads/assets/PyQtTodoMVCMac.png) | ![Ubuntu app](https://raw.githubusercontent.com/Jeff-Mott-OR/pyqt-todomvc/refs/heads/assets/PyQtTodoMVCUbuntu.png) | ![Windows app](https://raw.githubusercontent.com/Jeff-Mott-OR/pyqt-todomvc/refs/heads/assets/PyQtTodoMVCWindows.png) |

## But why?

For fun and no profit. When I learned C++, at first I put off learning a GUI library. But I was interested in and always meant to learn the Qt GUI library. It lets you write desktop GUIs once that will look native for each of the various OSes. Later, after I did a hobby project in Python, I stumbled upon PyQt -- a project that exposes the Qt C++ library in Python -- and I decided to dive in.

## Pre-built executables and installers

* Windows: [PyQtTodoMVCSetup.exe](https://github.com/Jeff-Mott-OR/pyqt-todomvc/releases/download/1.0.0/PyQtTodoMVCSetup.exe)
* Ubuntu: [PyQtTodoMVC.deb](https://github.com/Jeff-Mott-OR/pyqt-todomvc/releases/download/1.0.0/PyQtTodoMVC.deb)

## Reproducible builds with Vagrant

Build for other OSes by generating a VM from a vagrant configuration file. [More.](https://developer.hashicorp.com/vagrant/intro)

### Windows

    $ cd vagrant/windows-10
    $ vagrant up

If all goes well, your source directory will contain a Windows setup installer at `<pyqt-todo>/target/MyFbsAppSetup.exe`.

### Ubuntu

    $ cd vagrant/ubuntu-jammy
    $ vagrant up

If all goes well, your source directory will contain a Debian package installer at `<pyqt-todo>/target/MyFbsApp.deb`.

### MacOS

No VM for MacOS. Boo. You'll need to build for Mac the manual way.

## Manual build and run

1.

Get Python3.6. I used [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions.

The paid version of fbs works with the latest Python and PyQt, but the free version is limited to older versions. I'm using the free version here, so I have to use Python3.6 instead of Python3.12, and PyQt5 instead of PyQt6.

2.

    $ python -m venv venv

This creates a "virtual environment". It's similar to site_modules from npm. It will locally contain any packages you install. [More.](https://docs.python.org/3/library/venv.html)

3.

    $ source venv/bin/activate

Execute shell commands for the virtual environment. It adds stuff to your PATH and whatnot.

4.

    $ (venv) pip install -r requirements.txt

5.

    $ (venv) fbs run
