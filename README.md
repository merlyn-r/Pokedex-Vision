# Vision Pokédex

An AI-powered Pokémon identification application that uses a mobile camera to recognize Pokémon from images and display detailed Pokédex information.

The project combines a Flutter mobile application with a local Flask backend and a computer-vision recognition pipeline.

---

## Demo

### Video Demo

Watch the complete application workflow:

**Camera → Capture Pokémon → AI Recognition → Pokédex Result**

[Watch the Demo Video](https://drive.google.com/file/d/1mzXyZ5fkmaL7lIodjlnXbdu8TgCyjkbu/view?usp=drive_link)

> GitHub may not play large MP4 files directly inside the README. If that happens, upload the video separately to the repository and/or use a GitHub Release, YouTube, or Google Drive link.

---

##  Screenshots

### Camera Interface

The Flutter mobile application provides a live camera interface with a target frame for positioning the Pokémon.

![Camera Screen](<img width="660" height="609" alt="image" src="https://github.com/user-attachments/assets/26291b20-ab09-4b95-a2f8-6564fef2cfa0" />
)

### Pokémon Recognition

The captured image is sent to the local Flask backend, where the vision recognition pipeline identifies the Pokémon.

![Recognition Result](<img width="962" height="900" alt="image" src="https://github.com/user-attachments/assets/b9f73e82-dbce-4887-bbff-8d123021145c" />
)

### Pokédex Information

After identification, the application displays detailed information including:

- Pokémon name
- Pokédex number
- Type
- Category
- Description
- Abilities
- Height and weight
- Base statistics
- Evolution line
- Moveset
- Recognition confidence



---

# Features

## AI Pokémon Recognition

The application uses a computer-vision recognition pipeline to identify Pokémon from captured images.

The model returns multiple candidate predictions along with confidence scores.

## Mobile Camera Integration

The Flutter application provides:

- Live camera preview
- Automatic focus
- Image capture
- Camera permission handling
- Image upload to the backend

## Pokédex Information

Once a Pokémon is identified, the application retrieves detailed Pokédex information from the local Pokémon database.

## Local API

The Flutter application communicates with a Flask REST API running locally on a computer.

Example endpoint:

```text
POST /api/identify
