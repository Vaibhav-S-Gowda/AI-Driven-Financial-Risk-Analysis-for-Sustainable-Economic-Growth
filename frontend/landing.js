// ── Navigation (works inside Streamlit iframe sandbox) ──
function navigateTo(page) {
    if (page === 'signin' || page === 'login' || page === 'sign in') {
        // Push browser history so back button works
        try {
            var currentUrl = new URL(window.parent.location.href);
            window.parent.history.pushState({nav: 'landing'}, '', currentUrl.toString());
        } catch(he) {}

        // Bulletproof navigation: Click the hidden Streamlit button in the parent window.
        try {
            if (window.parent && window.parent.document) {
                var strBtns = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < strBtns.length; i++) {
                    if (strBtns[i].innerText.includes('hidden_login')) {
                        strBtns[i].click();
                        return;
                    }
                }
            }
        } catch (e) {
            console.warn("DOM button click fallback failed:", e);
        }

        // Fallback 2: Try direct URL replacement
        try {
            var url = new URL(window.parent.location.href);
            url.searchParams.set('nav', 'login');
            window.parent.location.href = url.toString();
        } catch (e) {
            console.error("Direct navigation failed:", e);
            var a = document.createElement('a');
            a.href = "?nav=login";
            a.target = "_parent";
            document.body.appendChild(a);
            a.click();
        }
    } else {
        var target = document.querySelector('#' + page) || document.querySelector(page);
        if (target) {
            var navHeight = document.querySelector('.navbar').offsetHeight || 0;
            var top = target.getBoundingClientRect().top + window.scrollY - navHeight - 16;
            window.scrollTo({ top: top, behavior: 'smooth' });
        }
    }
}

// Intersection Observer for scroll animations
document.addEventListener("DOMContentLoaded", function () {
    const observerOptions = { root: null, rootMargin: '0px', threshold: 0.15 };
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal-up, .reveal-scale').forEach(el => observer.observe(el));

    setTimeout(() => {
        document.querySelectorAll('.reveal-up, .reveal-scale').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom >= 0) {
                el.classList.add('is-visible');
            }
        });
    }, 100);
});

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (!href || href === '#') return;
        const target = document.querySelector(href);
        if (!target) return;
        e.preventDefault();
        const navHeight = document.querySelector('.navbar').offsetHeight;
        const top = target.getBoundingClientRect().top + window.scrollY - navHeight - 16;
        window.scrollTo({ top, behavior: 'smooth' });
    });
});