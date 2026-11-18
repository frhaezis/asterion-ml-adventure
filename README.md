# Asterion

**Learn Machine Learning Through Story**

Asterion is an offline educational Android visual novel that combines fantasy storytelling, interactive exploration, and practical Python programming.

Explore an elven world, meet four distinct characters, make story-driven choices, and develop programming and machine learning knowledge through a structured educational adventure.

**Project status:** Experimental Android release — under active development.

## ✨ Features

- **100 story episodes** across 10 chapters, combining narrative progression with technical learning.
- **40 hands-on Python exercises** executed locally using a real CPython interpreter.
- **Machine learning curriculum** covering fundamental concepts, neural networks, Transformers, RAG, and AI agents.
- **Four character routes** featuring dialogue, relationships, and narrative choices.
- **Illustrated fantasy environments** with exploration, character portraits, and a gallery.
- **Offline execution** without mandatory accounts, paid APIs, or external inference services.
- **Progress saving** with JSON export/import, backup recovery, and persistent code drafts.
- **Integrated learning support** with explanations, examples, hints, and automated checks.

## 🧠 Learning Experience

Each educational episode follows a structured learning sequence:

1. A story-driven introduction.
2. Technical concepts and prerequisites.
3. Step-by-step explanations and worked examples.
4. Interactive practice.
5. A transfer task using a different case.
6. Reflection and progression.

The curriculum includes introductory Python, machine learning fundamentals, model evaluation, and engineering concepts related to modern AI systems.

Python exercises run against functional tests, including edge cases and independent inputs.

The Android edition focuses on Python programming and conceptual ML learning. **It does not require PyTorch or perform full neural network training.**

For hands-on PyTorch experiments, see the companion Windows project: [Persian Fairytale](https://github.com/frhaezis/persian-fairytale).

## 📱 Android Requirements

- Android 8.0 or newer
- 64-bit ARM64 or x86_64 device
- Current Android System WebView

The application includes the Python runtime needed for offline programming exercises.

No registration, advertisements, subscriptions, or paid APIs are required.

## 🚀 Installation

When an APK is available in GitHub Releases:

1. Download the Android APK.
2. Open the downloaded file on your device.
3. Allow installation from the selected source if Android requests permission.
4. Install and launch Asterion.

**Note:** The current release uses a Russian-language interface. English localization is planned.

## 🏗️ Technical Architecture

Asterion combines a native Android host with web-based game interfaces and an embedded Python runtime.

| Component | Technology |
|---|---|
| Android application | Java, Android SDK, WebView |
| Game interface | HTML, CSS, JavaScript |
| Native Python execution | CPython 3.12.15, Chaquopy 17.2.0 |
| Browser-based Python | Pyodide 0.26.4 |
| Learning content | JSON curriculum and exercises |
| Progress storage | Local application storage |
| Automated validation | Python exercise validators |

The Android Python executor runs in a separate application process, allowing running code to be stopped or timed out. This process separation is not a security sandbox for untrusted programs.

### Repository Structure

| Directory | Description |
|---|---|
| `android/` | Native Android application and embedded runtime |
| `web/` | Game interface, story content, and Python exercises |
| `docs/` | Technical documentation and learning materials |
| `tests/` | Automated tests and validation |
| `tools/` | Build and development utilities |
| `README_RU.md` | Detailed Russian-language documentation |

## 🛠️ Building from Source

Building the Android application requires a suitable JDK and Android SDK.

Detailed instructions are available in [android/README.md](android/README.md).

Signing keys are not distributed with the project. Independently built applications must be signed with your own key, and they cannot update installations signed with a different key.

## 🧪 Testing and Limitations

The project includes automated checks for the curriculum, Python exercises, game progression, and Android integration.

Testing described in the project documentation includes an Android 15 x86_64 emulator, browser-based execution, and native Python validation.

Physical ARM64 device compatibility has not been independently verified in the documented test environment.

Automated test success does not establish educational effectiveness or guarantee that every device configuration will work.

See [docs/TEST_REPORT.md](docs/TEST_REPORT.md) for details.

## 🗺️ Future Development

Planned improvements include:

- English localization of the interface, lessons, and exercises.
- Improved responsive layouts for different phone and tablet screens.
- Better accessibility and navigation.
- Additional educational scenarios.
- Further testing on physical Android devices.
- Improvements to the learning experience and narrative presentation.

These are development goals rather than currently implemented features.

## 📚 Documentation

- [Russian README](README_RU.md)
- [Android build instructions](android/README.md)
- [Python execution and validation](docs/PYTHON.md)
- [Curriculum](docs/CURRICULUM.md)
- [Testing report](docs/TEST_REPORT.md)
- [Educational sources](docs/SOURCES.md)

---

**Asterion** is an experimental portfolio project exploring the intersection of interactive storytelling, mobile software development, and programming education.
