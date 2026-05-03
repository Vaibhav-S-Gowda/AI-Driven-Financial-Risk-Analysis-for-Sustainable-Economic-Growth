import streamlit as st
import os
import base64
import re
import streamlit.components.v1 as components

def push_nav_to_url(val: str):
    try:
        st.query_params["nav"] = val
    except Exception:
        pass

def render_landing():
    # Hidden button mechanism: Javascript will 'click' this if direct top-level navigation fails
    st.markdown("<div id='st-hidden-btn-container'>", unsafe_allow_html=True)
    if st.button("hidden_dashboard", key="landing_hidden_dashboard_trigger"):
        st.session_state["page"] = "dashboard"
        push_nav_to_url("dashboard")
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
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    landing_path = os.path.join(frontend_dir, "landing.html")
    css_path = os.path.join(frontend_dir, "landing.css")
    js_path = os.path.join(frontend_dir, "landing.js")
    
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
        
        # Embed images as base64 data URIs (iframe can't resolve relative paths)
        assets_dir = os.path.join(frontend_dir, "assets")
        def replace_asset_url(match):
            prefix = match.group(1)
            path = match.group(2)
            suffix = match.group(3)
            # Resolve the actual file path
            asset_path = os.path.join(assets_dir, os.path.basename(path))
            if not os.path.exists(asset_path):
                # Try the path as-is relative to frontend/
                asset_path = os.path.join(frontend_dir, path)
            if os.path.exists(asset_path):
                ext = os.path.splitext(asset_path)[1].lower()
                mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}.get(ext.lstrip("."), "image/png")
                with open(asset_path, "rb") as img_f:
                    b64 = base64.b64encode(img_f.read()).decode()
                return f"{prefix}data:{mime};base64,{b64}{suffix}"
            return match.group(0)
        
        # Match url('assets/...') and src="assets/..." patterns  
        html_content = re.sub(r"""(url\(['"]?)((?:\.?/?)assets/[^'")]+)(['"]?\))""", replace_asset_url, html_content)
        html_content = re.sub(r"""(src=['"])((?:\.?/?)assets/[^'"]+)(['"])""", replace_asset_url, html_content)
        html_content = re.sub(r"""(href=['"])((?:\.?/?)assets/[^'"]+)(['"])""", replace_asset_url, html_content)

        # Inject popstate listener for browser back/forward support
        popstate_script = """
<script>
(function() {
    try {
        window.parent.addEventListener('popstate', function() {
            var params = new URLSearchParams(window.parent.location.search);
            var nav = params.get('nav') || 'landing';
            if (nav !== 'landing') {
                window.parent.location.reload();
            }
        });
    } catch(e) {}
})();
</script>
"""
        html_content = html_content.replace('</body>', popstate_script + '</body>')
        
        components.html(html_content, scrolling=True, height=900)
    else:
        st.error("landing.html not found.")

    st.stop()