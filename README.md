# PyRDP

PyRDP is a Python Remote Desktop Protocol (RDP) Monster-in-the-Middle (MITM) tool and library.

![PyRDP Logo](https://raw.githubusercontent.com/GoSecure/pyrdp/main/docs/pyrdp-logo.svg?sanitize=true)

It features a few tools:
- RDP Monster-in-the-Middle
    - Logs plaintext credentials or NetNTLM hashes used when connecting
    - Steals data copied to the clipboard
    - Saves a copy of the files transferred over the network
    - Crawls shared drives in the background and saves them locally
    - Saves replays of connections so you can look at them later
    - Runs console commands or PowerShell payloads automatically on new connections
- RDP Player:
    - See live RDP connections coming from the MITM
    - View replays of RDP connections
    - Take control of active RDP sessions while hiding your actions
    - List the client's mapped drives and download files from them during active sessions
- Converter tool:
    - Convert RDP replays to videos for easier sharing
    - Convert RDP replays to a sequence of low-level events serialized in JSON format
    - Convert PCAPs to replays, videos or JSON events
    - Convert decrypted PCAPs (L7 PDUs) to replays, videos or JSON events
- RDP Certificate Cloner:
    - Create a self-signed X509 certificate with the same fields as an RDP server's certificate

PyRDP was [introduced in 2018](https://www.gosecure.net/blog/2018/12/19/rdp-man-in-the-middle-smile-youre-on-camera) in
which we [demonstrated that we can catch a real threat actor in
action](https://www.youtube.com/watch?v=eB7RC9FmL6Q). This tool is being developed with both pentest and malware
research use cases in mind.



## Table of Contents
- [PyRDP](#pyrdp)
  - [Table of Contents](#table-of-contents)
  - [Supported Systems](#supported-systems)
  - [Installing](#installing)
    - [Using the Docker Image](#using-the-docker-image)
  - [Using PyRDP](#using-pyrdp)
    - [Using the PyRDP Monster-in-the-Middle](#using-the-pyrdp-monster-in-the-middle)
      - [Using the GUI Player in Docker](#using-the-gui-player-in-docker)
      - [Converting videos in Docker](#converting-videos-in-docker)
  - [PyRDP Lore](#pyrdp-lore)
  - [Contributing to PyRDP](#contributing-to-pyrdp)
  - [Acknowledgements](#acknowledgements)


## Supported Systems
PyRDP should work on Python 3.7 and up on the x86-64, ARM and ARM64 platforms.

This tool has been tested to work on Python 3.7 on Linux (Ubuntu 20.04, 22.04), Raspberry Pi and Windows. It has not been tested on macOS.


## Installing

Two installation techniques are recommended via `pipx` or using docker containers.
Installing from source or building docker containers yourself is covered in the [development documentation](docs/devel.adoc).


### Using the Docker Image

This is the easiest installation method if you have docker installed and working.

```
docker pull 4ss078/pyrdp:latest
```

You can find the list of all our Docker images [on the gosecure/pyrdp DockerHub page](https://hub.docker.com/r/gosecure/pyrdp/tags).
The `latest` tag refers to the latest released version while the `devel` tag is the docker image built out of our `main` branch.


## Using PyRDP

### Using the PyRDP Monster-in-the-Middle
Use `pyrdp-mitm <ServerIP>` or `pyrdp-mitm <ServerIP>:<ServerPort>` to run the MITM.

Assuming you have an RDP server running on `192.168.1.10` and listening on port 3389, you would run:

```
pyrdp-mitm 192.168.1.10
```

When running the MITM for the first time a directory called `pyrdp_output/`
will be created relative to the current working directory.
Here is an example layout of that directory:

```
pyrdp_output/
├── certs
│   ├── WinDev2108Eval.crt
│   └── WinDev2108Eval.pem
├── files
│   ├── e91c6a5eb3ca15df5a5cb4cf4ebb6f33b2d379a3a12d7d6de8c412d4323feb4c
│   ├── b14b26b7d02c85e74ab4f0d847553b2fdfaf8bc616f7c3efcc4771aeddd55700
├── filesystems
│   ├── romantic_kalam_8214773
│   │   └── device1
│   │   └── clipboard
|           └── priv-esc.exe -> ../../../files/b14b26b7d02c85e74ab4f0d847553b2fdfaf8bc616f7c3efcc4771aeddd55700
│   └── happy_stonebraker_1992243
│       ├── device1
│       └── device2
|           └── Users/User/3D Objects/desktop.ini -> ../../../../../../e91c6a5eb3ca15df5a5cb4cf4ebb6f33b2d379a3a12d7d6de8c412d4323feb4c
├── logs
│   ├── crawl.json
│   ├── crawl.log
│   ├── mitm.json
│   ├── mitm.log
│   ├── mitm.log.2021-08-26
│   ├── ntlmssp.log
│   ├── player.log
│   └── ssl.log
└── replays
    ├── rdp_replay_20231214_01-20-28_965_happy_stonebraker_1992243.pyrdp
    └── rdp_replay_20231214_00-42-24_295_romantic_kalam_8214773.pyrdp
```

* `certs/` contains the certificates generated stored using the `CN` of the certificate as the file name
* `files/` contains all files captured and are deduplicated by saving them using the SHA-256 hash of the content as the filename
* `filesystems/` contains a recreation of the filesystem of the targets classified by session IDs.
   To save space on similar sessions, files are symbolic links to the actual files under `files/`.
* `logs/` contains all the various logs with most in both JSON and plaintext formats:
  * `crawl`: the file crawler log
  * `mitm`: the main MITM log
  * `ntlmssp.log`: the captured NetNTLM hashes
  * `player.log`: the player log
  * `ssl.log`: the TLS master secrets stored in a format compatible with Wireshark
* `replays/` contains all the previously recorded PyRDP sessions with timestamps and session IDs in the filename

#### Using the GUI Player in Docker

Using the player will require you to export the `DISPLAY` environment variable from the host to the docker.
This redirects the GUI of the player to the host screen.
You also need to expose the host's network and prevent Qt from using the MIT-SHM X11 Shared Memory Extension.
To do so, add the `-e` and `--net` options to the run command:

```
docker run -e DISPLAY=$DISPLAY -e QT_X11_NO_MITSHM=1 --net=host gosecure/pyrdp pyrdp-player
```

Keep in mind that exposing the host's network to docker can compromise the isolation between your container and the host.
If you plan on using the player, X11 forwarding using an SSH connection would be a more secure way.

#### Converting videos in Docker

The video conversion process relies on PyAV, ffmpeg and QT so you need the regular docker image not the slim one.

You need a volume mount (`-v`) to share files with the container.
Here we map our local directory with `/shared/` in the container.

```
docker run -e QT_QPA_PLATFORM=offscreen -v $PWD/:/shared gosecure/pyrdp pyrdp-convert -f mp4 <filename-relative-to-volume-in-/shared/> -o /shared/
```

The `QT_QPA_PLATFORM=offscreen` environment variable is required [due to a bug documented here](https://github.com/GoSecure/pyrdp/issues/428).
It tells to QT that it is correct that no display environment is available.


## PyRDP Lore

* [Introduction blog post](https://www.gosecure.net/blog/2018/12/19/rdp-man-in-the-middle-smile-youre-on-camera) in which we [demonstrated that we can catch a real threat actor in action](https://www.youtube.com/watch?v=eB7RC9FmL6Q)
* [Talk at NorthSec 2019](https://docs.google.com/presentation/d/1avcn8Sh2b3IE7AA0G9l7Cj5F1pxqizUm98IbXUo2cvY/edit#slide=id.g404b70030f_0_581) where two demos were performed:
  * [First demo](https://youtu.be/5JztJzi-m48): credential logging, clipboard stealing, client-side file browsing and a session take-over
  * [Second demo](https://youtu.be/bU67tj1RkMA): the execution of cmd or powershell payloads when a client successfully authenticates
* [PyRDP Logo](/docs/pyrdp-logo.png) licensed under CC-BY-SA 4.0.
* [BlackHat USA Arsenal 2019 Slides](https://docs.google.com/presentation/d/17P_l2n-hgCehQ5eTWilru4IXXHnGIRTj4ftoW4BiX5A/edit?usp=sharing)
* [DerbyCon 2019 Slides](https://docs.google.com/presentation/d/1UAiN2EZwDcmBjLe_t5HXB0LzbNclU3nnigC-XM4neIU/edit?usp=sharing) ([Video](https://www.youtube.com/watch?v=zgt3N6Nrnss))
* [Blog: PyRDP on Autopilot](https://www.gosecure.net/blog/2020/02/26/pyrdp-on-autopilot-unattended-credential-harvesting-and-client-side-file-stealing/)
* [Blog: PyRDP 1.0](https://www.gosecure.net/blog/2020/10/20/announcing-pyrdp-1-0/)
* [DefCon 2020 Demo Labs](https://www.youtube.com/watch?v=1q2Eo3x3u0g)
* [Blog: Capturing RDP NetNTLMv2 Hashes: Attack details and a Technical How-To Guide](https://www.gosecure.net/blog/2022/01/17/capturing-rdp-netntlmv2-hashes-attack-details-and-a-technical-how-to-guide/)
* [BlackHat USA Arsenal 2021 Slides](https://gosecure.github.io/presentations/2021-08-05_blackhat-usa/BlackHat-USA-21-Arsenal-PyRDP-OlivierBilodeau.pdf)
* [Presentation: I Watched You Roll the Die: Unparalleled RDP Monitoring Reveal Attackers' Tradecraft](http://i.blackhat.com/BH-US-23/Presentations/US-23-Bilodeau-I-Watched-You-Roll-the-Die-Unparalleled-RDP-Monitoring.pdf) at BlackHat USA 2023



## Contributing to PyRDP
See our [contribution guidelines](CONTRIBUTING.md).

## Acknowledgements
PyRDP uses code from the following open-source software:

- [RC4-Python](https://github.com/bozhu/RC4-Python) for the RC4 implementation.
- [rdesktop](https://github.com/rdesktop/rdesktop) for bitmap decompression.
- [rdpy](https://github.com/citronneur/rdpy) for RC4 keys, the bitmap decompression bindings and the base GUI code for
the PyRDP player.
- [FreeRDP](https://github.com/FreeRDP/FreeRDP) for the scan code enumeration.
