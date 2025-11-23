import streamlit as st
import json
from scorer import TranscriptScorer

st.set_page_config(page_title="Student Introduction Scorer", page_icon="🎤", layout="wide")

# Title and description
st.title("🎤 Student Introduction Transcript Scorer")
st.markdown("""
This tool analyzes spoken self-introduction transcripts and provides scores based on multiple criteria:
- **Salutation**: Greeting quality
- **Content & Structure**: Key information and flow
- **Speech Rate**: Words per minute
- **Language & Grammar**: Grammar and vocabulary
- **Clarity**: Filler word usage
- **Engagement**: Emotional tone
""")

# Initialize scorer
scorer = TranscriptScorer()

# Sidebar with sample transcript
with st.sidebar:
    st.header("Sample Transcript")
    sample_transcript = """Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. 
I am 13 years old. I live with my family. There are 3 people in my family, me, my mother and my father.
One special thing about my family is that they are very kind hearted to everyone and soft spoken. One thing I really enjoy is play, playing cricket and taking wickets.
A fun fact about me is that I see in mirror and talk by myself. One thing people don't know about me is that I once stole a toy from one of my cousin.
 My favorite subject is science because it is very interesting. Through science I can explore the whole world and make the discoveries and improve the lives of others. 
Thank you for listening."""
    
    if st.button("Load Sample Transcript"):
        st.session_state.transcript = sample_transcript

# Main input area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Input Transcript")
    transcript_input = st.text_area(
        "Paste the student's self-introduction transcript here:",
        value=st.session_state.get('transcript', ''),
        height=250,
        placeholder="Enter or paste the transcript text here..."
    )
    
    # Optional: estimated duration for WPM calculation
    duration = st.number_input(
        "Estimated speech duration (minutes) - Optional:",
        min_value=0.5,
        max_value=10.0,
        value=1.5,
        step=0.5,
        help="If you know the audio duration, enter it here for accurate WPM calculation"
    )

with col2:
    st.subheader("Settings")
    show_details = st.checkbox("Show detailed breakdown", value=True)
    show_keywords = st.checkbox("Show found keywords", value=True)

# Score button
if st.button("🎯 Score Transcript", type="primary", use_container_width=True):
    if not transcript_input.strip():
        st.error("Please enter a transcript to score!")
    else:
        with st.spinner("Analyzing transcript..."):
            # Get results
            results = scorer.score_transcript(transcript_input, duration)
            
            # Display overall score
            st.markdown("---")
            st.subheader("📊 Results")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.metric("Overall Score", f"{results['overall_score']:.1f}/100")
            with col2:
                st.metric("Word Count", results['word_count'])
            with col3:
                if 'wpm' in results:
                    st.metric("WPM", f"{results['wpm']:.0f}")
            
            # Display per-criterion scores
            st.markdown("---")
            st.subheader("📋 Detailed Criterion Scores")
            
            for criterion in results['criteria']:
                with st.expander(f"**{criterion['name']}** - Score: {criterion['score']:.1f}/{criterion['max_score']}", expanded=show_details):
                    # Progress bar - Convert to float to avoid numpy float32 issues
                    progress = float(criterion['score'] / criterion['max_score']) if criterion['max_score'] > 0 else 0.0
                    st.progress(progress)
                    
                    # Feedback
                    st.markdown(f"**Feedback:** {criterion['feedback']}")
                    
                    # Details
                    if show_details and 'details' in criterion:
                        st.markdown("**Details:**")
                        for key, value in criterion['details'].items():
                            st.write(f"- {key}: {value}")
                    
                    # Keywords found
                    if show_keywords and 'keywords_found' in criterion:
                        if criterion['keywords_found']:
                            st.success(f"✓ Keywords found: {', '.join(criterion['keywords_found'])}")
                        else:
                            st.warning("✗ No relevant keywords found")
            
            # JSON output section
            st.markdown("---")
            st.subheader("📄 JSON Output")
            with st.expander("View/Copy JSON Output"):
                json_output = json.dumps(results, indent=2)
                st.code(json_output, language='json')
                st.download_button(
                    label="Download JSON",
                    data=json_output,
                    file_name="transcript_score.json",
                    mime="application/json"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Built for Nirmaan Education AI Internship Case Study</p>
</div>
""", unsafe_allow_html=True)
