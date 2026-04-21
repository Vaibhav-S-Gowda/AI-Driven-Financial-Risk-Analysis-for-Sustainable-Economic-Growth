function navigateTo(page) {
    // Push browser history so back button works
    try {
        var currentUrl = new URL(window.parent.location.href);
        window.parent.history.pushState({nav: 'login'}, '', currentUrl.toString());
    } catch(he) {}

    try {
        if (window.parent && window.parent.document) {
            var strBtns = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < strBtns.length; i++) {
                var btnText = strBtns[i].innerText;
                if (page === 'dashboard' && btnText.includes('Sign in')) {
                    strBtns[i].click();
                    return;
                }
                if (page === 'landing' && btnText.includes('Back to Home')) {
                    strBtns[i].click();
                    return;
                }
            }
        }
    } catch(e) { console.warn("DOM navigation failed:", e); }

    // Fallback
    try {
        var url = new URL(window.parent.location.href);
        url.searchParams.set('nav', page);
        window.parent.location.href = url.toString();
    } catch (e) {
        var a = document.createElement('a');
        a.href = "?nav=" + page;
        a.target = "_parent";
        document.body.appendChild(a);
        a.click();
    }
}

function handleSignIn() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btn = document.getElementById('signin-btn');

    if (!email || !password) {
        ['email','password'].forEach(id => {
            const el = document.getElementById(id);
            el.style.borderColor = '#f87171';
            setTimeout(() => { el.style.borderColor = ''; }, 1500);
        });
        return;
    }

    // Extract name from email (e.g. alex@finrisk.ai -> Alex)
    let rawName = email.split('@')[0];
    let displayName = rawName.charAt(0).toUpperCase() + rawName.slice(1).toLowerCase();
    
    // Store in localStorage for the dashboard to pick up
    localStorage.setItem('finrisk_username', displayName);

    btn.classList.add('loading');
    setTimeout(() => { navigateTo('dashboard'); }, 800);
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') handleSignIn();
});