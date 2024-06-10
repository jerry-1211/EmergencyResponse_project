
window.addEventListener('DOMContentLoaded', event => {

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };

    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );

    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Add event listeners for showing and hiding the navbar collapse
    const navbarResponsive = document.getElementById('navbarResponsive');
    navbarResponsive.addEventListener('shown.bs.collapse', () => {
        mainNav.classList.add('navbar-expanded');
    });
    navbarResponsive.addEventListener('hidden.bs.collapse', () => {
        mainNav.classList.remove('navbar-expanded');
    });
});
