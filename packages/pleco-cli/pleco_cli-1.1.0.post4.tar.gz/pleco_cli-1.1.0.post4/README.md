# 🐟 pleco

**pleco** is a minimal Python CLI tool for ingesting and cleaning ROV serial data from NMEA sentences.

It reads from a serial port (e.g. `/dev/ttyUSB0`, `COM3`, `COM5` etc.), writes the raw feed to a CSV, and periodically extracts structured data from specified NMEA sentences into a cleaned CSV file.

---

## 🚀 Installation


Install with [`pip`](https://pipx.pypa.io/) (recommended):

```bash
pip install pleco-cli
