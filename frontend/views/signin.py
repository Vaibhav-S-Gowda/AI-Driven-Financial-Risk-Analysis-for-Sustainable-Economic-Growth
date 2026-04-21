import streamlit as st
import os
import streamlit.components.v1 as components

def push_nav_to_url(val: str):
    try:
        st.query_params["nav"] = val
    except Exception:
        pass

def render_signin():
    st.markdown("""<style>
        [data-testid='stSidebar'], [data-testid='stHeader'], footer { display:none !important; }
        .block-container { padding:0 !important; max-width:100% !important; margin:0 !important; }
        .main { padding:0 !important; }
        .main > div { padding:0 !important; }
        [data-testid='stAppViewContainer'] { background:#ffffff !important; }
        .stApp, .main { scrollbar-width:none !important; -ms-overflow-style:none !important; }
        iframe { width:100% !important; border:none !important; display:block !important; }

        /* ── Signin page nav buttons ── */
        [data-testid='stHorizontalBlock']:first-of-type {
            background: #ffffff;
            padding: 1rem 5% !important;
            position: sticky;
            top: 0;
            z-index: 999;
        }
        div[data-testid='stHorizontalBlock']:first-of-type button {
            border-radius: 100px !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            padding: 0.5rem 1.4rem !important;
            font-family: 'Inter', system-ui, sans-serif !important;
            transition: all 0.2s !important;
        }
        /* Back button */
        div[data-testid='stHorizontalBlock']:first-of-type div:nth-child(2) button {
            background: transparent !important;
            border: 1.5px solid #E5E7EB !important;
            color: #111827 !important;
        }
        div[data-testid='stHorizontalBlock']:first-of-type div:nth-child(2) button:hover {
            background: #F7F9FA !important; border-color: #0ecfab !important; color: #0ecfab !important;
        }
        /* Sign in button */
        div[data-testid='stHorizontalBlock']:first-of-type div:last-child button {
            background: #111827 !important;
            border: none !important;
            color: white !important;
        }
        div[data-testid='stHorizontalBlock']:first-of-type div:last-child button:hover {
            background: #0ecfab !important;
        }
    </style>""", unsafe_allow_html=True)

    # ── Streamlit-native nav bar ──
    nav_c1, nav_c2, nav_c3 = st.columns([6, 1.5, 1.5])
    with nav_c1:
        st.markdown("<div style='font-weight:700;font-size:1.25rem;color:#111827;padding:0.4rem 0;font-family:Inter,sans-serif;'><span style='color:#0ecfab;margin-right:8px;'>◈</span> FinRisk AI</div>", unsafe_allow_html=True)
    with nav_c2:
        if st.button("← Back to Home", key="signin_back"):
            st.session_state.page = "landing"
            push_nav_to_url("landing")
            st.rerun()
    with nav_c3:
        if st.button("Sign in →", key="signin_go"):
            st.session_state.page = "dashboard"
            push_nav_to_url("dashboard")
            st.rerun()

    # ── Sign-in page content (with its navbar hidden) ──
    signin_path = os.path.join(os.path.dirname(__file__), "..", "signin.html")
    css_path = os.path.join(os.path.dirname(__file__), "..", "signin.css")
    js_path = os.path.join(os.path.dirname(__file__), "..", "signin.js")
    
    if os.path.exists(signin_path):
        with open(signin_path, "r", encoding="utf-8") as f:
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
        
        html_content = html_content.replace(
            '<nav class="navbar">',
            '<nav class="navbar" style="display:none !important;">'
        )
        
        # Inject popstate listener for browser back/forward support
        popstate_script = """
<script>
(function() {
    try {
        window.parent.addEventListener('popstate', function() {
            var params = new URLSearchParams(window.parent.location.search);
            var nav = params.get('nav') || 'landing';
            if (nav !== 'login') {
                window.parent.location.reload();
            }
        });
    } catch(e) {}
})();
</script>
"""
        html_content = html_content.replace('</body>', popstate_script + '</body>')
        
        components.html(html_content, height=900, scrolling=True)
    else:
        st.error("signin.html not found.")
    st.stop()
