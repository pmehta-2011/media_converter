import streamlit as st
import moviepy.editor as mp
import os
import speech_recognition as sr

#Streamlit
st.title("MEDIA Converter")

uploaded_video = st.file_uploader("Upload a Video File", type=["mp4", "mkv", "avi", "mov"])

trim_range = st.slider("Select the range of seconds to keep:", 0, 300, (5, 30))

audio_folder = "audio"
os.makedirs(audio_folder, exist_ok=True)

def sanitize_filename(filename):
    return filename.replace(" ", "_")

def extract_audio(video_file, trim_start, trim_end):
    try:
        video_path = os.path.join(audio_folder, sanitize_filename(video_file.name))
        with open(video_path, "wb") as f:
            f.write(video_file.getbuffer())

        video_clip = mp.VideoFileClip(video_path)

        #Trim range should be valid to perform it------
        if trim_start >= trim_end or trim_end > video_clip.duration:
            raise ValueError("Invalid trim range selected.")

        video_clip = video_clip.subclip(trim_start, trim_end)

        audio_filename = sanitize_filename(f"{os.path.splitext(video_file.name)[0]}.wav")
        audio_path = os.path.join(audio_folder, audio_filename)
        video_clip.audio.write_audiofile(audio_path)

        video_clip.close()
        return audio_path
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return ""

if uploaded_video:
    st.write("Processing video...")
    with st.spinner("Extracting audio..."):
        audio_path = extract_audio(uploaded_video, trim_range[0], trim_range[1])

        if audio_path:
            st.success("Audio extracted successfully!")
            st.subheader("Download Extracted Audio")
            with open(audio_path, "rb") as audio_file:
                st.download_button(
                    label="Download Audio",
                    data=audio_file,
                    file_name=os.path.basename(audio_path),
                    mime="audio/wav"
                )
            if st.button("Transcribe Audio"):
                with st.spinner("Transcribing..."):
                    text = transcribe_audio(audio_path)
                    if text:
                        st.success("Transcription Complete!")
                        st.subheader("Transcribed Text")
                        st.write(text)

                        # Allow download of transcribed text
                        st.download_button(
                            label="Download Transcription",
                            data=text,
                            file_name="transcription.txt",
                            mime="text/plain"
                        )
            os.remove(audio_path)
            os.remove(os.path.join(audio_folder, sanitize_filename(uploaded_video.name)))
