"""Keep the current DOM visible while Streamlit processes an interaction."""
from pathlib import Path
import uuid
import streamlit as st
import streamlit.components.v1 as components
_SCRIPT = (Path(__file__).parent / 'assets' / 'ui_transition.js').read_text(encoding='utf-8')
def install_transition_guard():
    with st.container(key='transition_bridge'):
        components.html('<script>'+_SCRIPT+'</script>',height=0,width=0)
    st.markdown('<style>.st-key-transition_bridge{height:0!important;min-height:0!important;margin:0!important;padding:0!important;overflow:hidden}</style>',unsafe_allow_html=True)


def mark_render_complete():
    st.markdown('<span data-sg-render-token="'+uuid.uuid4().hex+'" style="display:none"></span>',unsafe_allow_html=True)
