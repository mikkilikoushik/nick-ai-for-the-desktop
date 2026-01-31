About
This project is a Python-based voice assistant that integrates speech recognition, text-to-speech, and automation features to provide a hands-free experience for everyday tasks. Built using libraries such as speech_recognition, pyttsx3, wikipedia, and webbrowser, the assistant listens to user commands, interprets them, and executes actions ranging from retrieving summaries to opening applications.

Key Features
Voice Interaction: Uses Google’s speech recognition API to capture and process spoken commands.

Text-to-Speech Output: Provides spoken responses via pyttsx3, ensuring a natural conversational flow.

Information Retrieval: Fetches concise summaries from Wikipedia based on user queries.

System Utilities: Opens Bluetooth settings, reports the current date and time, and launches YouTube directly from voice commands.

Custom Commands: Includes flexible triggers like “start summary,” “come back,” “stop,” and more for intuitive control.

How It Works
The assistant greets the user and enters listening mode.

Spoken input is processed and matched against predefined commands.

Depending on the command, the assistant either speaks back information, executes a system action, or retrieves online content.

The loop continues until the user says “stop,” at which point the assistant gracefully exits.

Purpose
This project demonstrates how voice-driven automation can be implemented with Python, bridging natural language processing and everyday utility. It is ideal for learners exploring speech recognition, NLP basics, and automation scripting, while also serving as a foundation for building more advanced AI-powered assistants.
