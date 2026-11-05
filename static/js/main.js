// Main JavaScript for DMI Class of 2027 Awards Nomination System
document.addEventListener('DOMContentLoaded', () => {
    // Mobile navigation toggle
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Auto-dismiss success and info toasts after 6 seconds
    const toasts = document.querySelectorAll('[role="alert"]');
    toasts.forEach((toast) => {
        setTimeout(() => {
            if (toast && toast.parentElement) {
                toast.style.transition = 'opacity 0.5s ease-out';
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 500);
            }
        }, 6000);
    });
});

