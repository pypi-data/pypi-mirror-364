# Installation

## Pipx

Pipx can install Python programs, automatically installing dependencies in a virtual environment.

First install pipx using your system package manager, e.g. `sudo apt install pipx` or `sudo dnf install pipx`.

Then, run:

```
pipx install 'raphson-mp[online]'
```
or
```
pipx install 'raphson-mp[offline]'
```
depending on whether you are planning to use the music player in online mode or offline mode (connected to another server). In both cases the same package is installed, but with a specific set of dependencies.

The music player is now available as the command `raphson-mp`.

Unless you are using the music player only in offline mode, you should also install:
* Debian: `sudo apt install ffmpeg libchromaprint-tools`
* Fedora: `sudo dnf install ffmpeg chromaprint-tools`

Start the server: `raphson-mp start`.

The music player uses two configurable directories to store data, [--data-dir](./databases.md) and [--music-dir](./music-files.md) which are documented by the linked pages.

## Container

Take the `compose.prod.yaml` compose file as a starting point.

Management tasks can be performed by running a second instance of the container:
```
docker compose run music --help
```

# Usage

Run `raphson-mp --help` for help.

Start the web server: `raphson-mp start`

Create an admin user: `raphson-mp useradd --admin yourusername`

Scan for file changes, if you've modified files directly: `raphson-mp scan`
