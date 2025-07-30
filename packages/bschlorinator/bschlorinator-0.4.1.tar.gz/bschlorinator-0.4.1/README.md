# Chlorinator Control System with Raspberry Pi and Telit LE50-433

This project provides a Python-based control and monitoring system for a chlorinator device, using a Raspberry Pi and a Telit LE50-433 RF module. The system communicates with the chlorinator over a serial interface, reads real-time sensor data (pH, ORP, temperature, salinity, etc.), and can control relays for various automation tasks.

## Features

- Communicates with a chlorinator over UART serial
- RF communication via Telit LE50-433 module
- Relay control for switching devices
- Collects and logs sensor data (pH, ORP, PPM, Temperature, etc.)
- Compatible with Raspberry Pi 3 and 4

## Hardware

- Raspberry Pi 3 or 4 (tested)
- Telit LE50-433 radio module (Was packaged with my BS Pool Evolink 35 on raspberry PI)
- Chlorinator with serial protocol (BS Pool Evolink 35 Tested)
- Relays connected via GPIO

## Usage

- pip install bschlorinator

## Contributions

Feel free to open issues or submit pull requests!