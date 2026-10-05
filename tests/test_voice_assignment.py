from ai_dubbing.tts.voice_assignment import assign_voice, assign_voices


def test_voice_assignment_is_stable_and_complete() -> None:
    assert assign_voice("Kai") == assign_voice("Kai")
    mapping = assign_voices(["Kai", "Mira", "Kai", None])
    assert set(mapping) == {"Kai", "Mira", "narrator"}
