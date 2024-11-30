import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
import av

from settings import (
    get_barbell_curl,
    get_bent_over_dumbbell_row,
    get_squat_with_weights
)
from activity import Activity
from utils import get_mediapipe_pose

# --------------------- Custom CSS for Background and Styling ---------------------
def set_custom_styles():
    st.markdown(
        """
        <style>
        /* Set the overall background color */
        body {
            background-color: #e6f7ff;  /* Light blue background */
        }

        /* Style the main container */
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        /* Style the header */
        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: white !important; /* Make all text white */
        }

        /* Style the radio buttons */
        .stRadio > div {
            display: flex;
            flex-direction: column; /* Align options vertically */
            align-items: flex-start; /* Left-align the radio options */
            gap: 0.5rem; /* Add space between options */
        }

        /* Style the WebRTC streamer container */
        .webrtc-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 2rem;
        }

        /* Style the buttons */
        .stButton > button {
            background-color: #0073e6;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 5px;
            cursor: pointer;
        }

        .stButton > button:hover {
            background-color: #005bb5;
        }

        /* Responsive video */
        video {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Apply the custom styles
set_custom_styles()

# --------------------- Application Initialization ---------------------
# Set the title of the Streamlit application with an emoji for visual appeal
st.title('🏋️‍♂️ Weight Training Analysis')

# --------------------- Sidebar for Configuration ---------------------
st.sidebar.header('🔧 Configuration')

# Exercise Selection Interface in Sidebar
exercise_options = ['Barbell Curl', 'Bent Over Dumbbell Row', 'Squat with Weights']
selected_activity = st.sidebar.radio(
    'Select Activity',
    exercise_options,
    horizontal=True
)

# Retrieve settings based on chosen activity
settings_map = {
    'Barbell Curl': get_barbell_curl,
    'Bent Over Dumbbell Row': get_bent_over_dumbbell_row,
    'Squat with Weights': get_squat_with_weights
}

settings = settings_map[selected_activity]()

# Initialize Activity Processor with settings
activity_processor = Activity(settings=settings, flip_frame=True)

# Initialize Mediapipe Pose Detector
pose_detector = get_mediapipe_pose()

# --------------------- Main Content Area ---------------------
st.markdown("---")  # Horizontal divider for separation

# Container for WebRTC Streamer
with st.container():
    st.subheader('🎥 Live Video Feed')
    st.markdown(
        """
        <div class="webrtc-container">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Configure and launch WebRTC streamer
    webrtc_streamer(
        key='ai-weight-training-coach',
        video_frame_callback=lambda frame: process_frame(frame, selected_activity, activity_processor, pose_detector),
        rtc_configuration={
            'iceServers': [
                {'urls': ['stun:stun.l.google.com:19302']}
            ]
        },
        media_stream_constraints={
            'video': {'width': {'min': 640, 'ideal': 640}},
            'audio': False
        },
        video_html_attrs=VideoHTMLAttributes(
            autoPlay=True,
            controls=False,
            width=720,
            muted=False
        )
    )

# --------------------- Frame Processing Function ---------------------
def process_frame(frame: av.VideoFrame, activity: str, processor: Activity, pose_det: any) -> av.VideoFrame:
    """
    Callback function to process each video frame.

    Args:
        frame (av.VideoFrame): The incoming video frame.
        activity (str): The selected exercise activity.
        processor (Activity): The activity processor instance.
        pose_det (any): The Mediapipe pose detector instance.

    Returns:
        av.VideoFrame: The processed video frame.
    """
    # Convert frame to RGB format
    image = frame.to_ndarray(format='rgb24')
    
    # Process the frame based on the selected activity
    if activity == 'Barbell Curl':
        processed_image, _ = processor.process_barbell_curl(image, pose_det)
    elif activity == 'Bent Over Dumbbell Row':
        processed_image, _ = processor.process_bent_over_dumbbell_row(image, pose_det)
    elif activity == 'Squat with Weights':
        processed_image, _ = processor.process_squat_with_weights(image, pose_det)
    else:
        processed_image = image  # Fallback to original image if activity not recognized
    
    # Convert processed image back to VideoFrame
    return av.VideoFrame.from_ndarray(processed_image, format='rgb24')
