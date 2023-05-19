# Stable Diffusion Public Demo Extension

This extension allows to turn the [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
into simple tech demo for public which exposes only the prompt, and keeps all the other configuration hidden.
It is meant to be run in Windows Kiosk mode so users could not tamper with the program.

If you want to use it for public on public place, it's recommended to be used along with 
[DiffusionDefender](https://github.com/WildBanjos/DiffusionDefender) which lets you blacklist some words from the prompt
(while allowing these words in the hard-coded negative prompt).

## Installation

Install it using the web UI, which is the simplest way.

## Features

This extension performs following modifications:
- It replaces the original footer with different one, most of the contents is the same, but the links are not clickable,
which is important for Kiosk mode.
- It hides the negative prompt from the UI, but keeps it in the generated images.
- Enlarges the important texts 2x so people can see it better.

It also adds feature for easy sharing of generated images. This extension provides functionality for generating QR code
for every generated image, next to the image, which points to the image path in output directory under some URL.
If you run basic webserver for serving static content inside the `outputs/txt2img-images`, the QR code will 
point to URL of this webserver, if properly configured.
