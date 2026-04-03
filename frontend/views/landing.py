import streamlit as st
import os
import streamlit.components.v1 as components

def push_nav_to_url(val: str):
    try:
        st.query_params["nav"] = val
    except Exception:
        pass

def render_landing():
    # Hidden button mechanism: Javascript will 'click' this if direct top-level navigation fails
    st.markdown("<div id='st-hidden-btn-container'>", unsafe_allow_html=True)
    if st.button("hidden_login", key="landing_hidden_login_trigger"):
        st.session_state["page"] = "login"
        push_nav_to_url("login")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Hide all Streamlit chrome + the hidden button
    st.markdown("""
    <style>
        [data-testid='stSidebar'], [data-testid='stHeader'], footer { display:none !important; }

        /* Remove ALL top spacing that causes the gap above the iframe */
        .block-container,
        [data-testid='stMainBlockContainer'],
        [data-testid='stAppViewBlockContainer'] {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        .main,
        .main > div,
        [data-testid='stAppViewContainer'],
        [data-testid='stVerticalBlock'],
        section[data-testid='stMain'] {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0 !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        /* Kill the gap between stVerticalBlock children */
        [data-testid='stVerticalBlock'] > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        iframe {
            width: 100vw !important;
            height: 100vh !important;
            max-height: 100vh !important;
            border: none !important;
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Completely collapse the hidden button container */
        #st-hidden-btn-container { display: none !important; height: 0 !important; overflow: hidden !important; }
        div[data-testid="stButton"] { display: none !important; height: 0 !important; overflow: hidden !important; position: absolute; left: -9999px; }
        /* Collapse any empty element spacers Streamlit injects */
        [data-testid='stVerticalBlockBorderWrapper'] { padding: 0 !important; margin: 0 !important; gap: 0 !important; }
    </style>
    """, unsafe_allow_html=True)


    # Listener removed: direct navigation handled within landing.html

    # Render the landing page HTML
    base_dir = os.path.dirname(__file__)
    landing_path = os.path.join(base_dir, "..", "landing.html")
    css_path = os.path.join(base_dir, "..", "landing.css")
    js_path = os.path.join(base_dir, "..", "landing.js")
    
    if os.path.exists(landing_path):
        with open(landing_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        css_content, js_content = "", ""
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f"<style>{f.read()}</style>"
        if os.path.exists(js_path):
            with open(js_path, "r", encoding="utf-8") as f:
                js_content = f"<script>{f.read()}</script>"
                
        html_content = html_content.replace('<!-- CSS_INJECTION_HOOK -->', css_content)
        html_content = html_content.replace('<!-- JS_INJECTION_HOOK -->', js_content)
        
        components.html(html_content, scrolling=True, height=900)
    else:
        st.error("landing.html not found.")

    st.stop()