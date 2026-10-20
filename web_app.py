import os
import sys
import time
import ssl
import importlib
import static_ffmpeg
import streamlit as st

# Ensure ffmpeg binary is in system PATH for Whisper and ffmpeg rendering
static_ffmpeg.add_paths()

# Fix potential SSL certificate verify issues on macOS Python
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

st.set_page_config(
    page_title="AI Auto Karaoke Generator",
    page_icon="🎤",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #FF4B4B;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 1.1rem;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎤 AI Auto Karaoke Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Tự động tải, bóc tách beat sạch bằng Demucs AI và tạo chữ Karaoke chạy theo nhịp từ bất kỳ link YouTube nào.</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Cấu hình AI")
    whisper_model = st.selectbox(
        "Mô hình Whisper (Nhận diện lời)",
        options=["base", "small", "tiny", "medium"],
        index=0,
        help="Mô hình càng lớn thì độ chính xác càng cao nhưng xử lý lâu hơn. 'base' là cân bằng nhất."
    )
    language = st.selectbox(
        "Ngôn ngữ bài hát",
        options=["vi", "en", "auto"],
        format_func=lambda x: "Tiếng Việt (vi)" if x == "vi" else ("Tiếng Anh (en)" if x == "en" else "Tự động nhận diện"),
        index=0
    )
    demucs_model = st.selectbox(
        "Mô hình tách Beat (Demucs)",
        options=["htdemucs"],
        index=0
    )
    st.divider()
    st.markdown("""
    **💡 Hướng dẫn nhanh:**
    1. Dán đường dẫn YouTube bài hát bạn thích.
    2. Bấm nút **Bắt đầu tạo Karaoke**.
    3. Chờ AI xử lý xong, bạn có thể xem trực tiếp hoặc tải video về máy!
    """)

# Main input section
youtube_url = st.text_input("🔗 Nhập đường link bài hát YouTube:", placeholder="https://www.youtube.com/watch?v=...")

col_btn, col_empty = st.columns([1, 2])
with col_btn:
    start_btn = st.button("🚀 Bắt đầu tạo Video Karaoke")

if start_btn:
    if not youtube_url.strip():
        st.warning("Vui lòng nhập đường link YouTube hợp lệ trước khi bắt đầu!")
    else:
        output_base = "output"
        os.makedirs(output_base, exist_ok=True)

        status_box = st.status("Đang khởi động quy trình AI...", expanded=True)
        progress_bar = st.progress(0)
        
        try:
            # Step 1: Download
            status_box.update(label="[1/4] Đang tải video & audio từ YouTube...")
            progress_bar.progress(15)
            import downloader
            importlib.reload(downloader)
            media_info = downloader.download_youtube(youtube_url, output_dir=os.path.join(output_base, "downloads"))
            song_id = media_info["id"]
            song_title = media_info["title"]
            video_path = media_info["video_path"]
            audio_path = media_info["audio_path"]
            st.write(f"✓ Đã tải: **{song_title}**")

            # Step 2: Separate audio
            status_box.update(label="[2/4] Đang tách beat bằng AI Demucs (Meta)...")
            progress_bar.progress(40)
            import separator
            importlib.reload(separator)
            stems = separator.separate_audio(
                audio_path=audio_path,
                output_dir=os.path.join(output_base, "separated"),
                model_name=demucs_model
            )
            vocals_path = stems["vocals_path"]
            beat_path = stems["beat_path"]
            st.write("✓ Bóc tách Beat và Giọng hát hoàn tất.")

            # Step 3: Whisper transcription & word timing
            status_box.update(label="[3/4] Đang phân tích mốc thời gian từng từ bằng Whisper AI...")
            progress_bar.progress(70)
            import transcriber
            import sub_generator
            importlib.reload(transcriber)
            importlib.reload(sub_generator)
            segments = transcriber.transcribe_audio(
                audio_path=vocals_path,
                model_size=whisper_model,
                language=language if language != "auto" else None
            )
            ass_path = os.path.join(output_base, f"{song_id}_karaoke.ass")
            sub_generator.generate_ass_karaoke(segments, ass_path, title=song_title)
            st.write("✓ Đã sinh file phụ đề Karaoke (.ass) với hiệu ứng đổi màu mượt mà.")

            # Step 4: Render final video
            status_box.update(label="[4/4] Đang tổng hợp và xuất Video Karaoke...")
            progress_bar.progress(90)
            import renderer
            importlib.reload(renderer)
            final_video_path = os.path.join(output_base, f"{song_id}_karaoke.mp4")
            renderer.render_karaoke_video(
                background_video=video_path,
                beat_audio=beat_path,
                ass_subtitles=ass_path,
                output_video=final_video_path
            )

            progress_bar.progress(100)
            status_box.update(label="🎉 Hoàn tất toàn bộ quy trình!", state="complete", expanded=False)

            # Display Results
            st.success(f"Video Karaoke cho bài hát **{song_title}** đã sẵn sàng!")
            
            tab1, tab2, tab3 = st.tabs(["🎬 Video Karaoke", "🎵 Nghe Beat Đã Tách", "📝 Phụ đề Karaoke (.ass)"])

            with tab1:
                st.video(final_video_path)
                with open(final_video_path, "rb") as vf:
                    st.download_button(
                        label="⬇️ Tải Video Karaoke (.mp4)",
                        data=vf,
                        file_name=f"{song_id}_karaoke.mp4",
                        mime="video/mp4"
                    )

            with tab2:
                col_beat, col_vocal = st.columns(2)
                with col_beat:
                    st.markdown("**Beat Nhạc (Instrumental):**")
                    st.audio(beat_path)
                with col_vocal:
                    st.markdown("**Giọng hát bóc tách (Acapella):**")
                    st.audio(vocals_path)

            with tab3:
                with open(ass_path, "r", encoding="utf-8") as af:
                    ass_content = af.read()
                st.text_area("Nội dung tệp .ass (với thẻ \\kf):", ass_content, height=250)
                st.download_button(
                    label="⬇️ Tải file phụ đề (.ass)",
                    data=ass_content,
                    file_name=f"{song_id}_karaoke.ass",
                    mime="text/plain"
                )

        except Exception as e:
            progress_bar.empty()
            status_box.update(label="❌ Có lỗi xảy ra trong quá trình xử lý", state="error")
            st.error(f"Chi tiết lỗi: {str(e)}")
