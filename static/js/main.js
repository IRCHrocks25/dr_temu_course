// Main JavaScript for Line Training

// Smooth scrolling
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth transitions to all interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .coach-card-btn');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        el.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});
