function navigateTo(page) {
    if (page === 'signin') page = 'login';
    window.parent.postMessage({ type: 'finrisk-nav', page: page }, '*');
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