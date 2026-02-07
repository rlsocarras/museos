// museo_effects.js - Versión sin jQuery
function initMuseoEffects() {
    // Carrusel básico
    const carousel = document.getElementById('galeriaCarousel');
    if (carousel) {
        const container = document.getElementById('carouselContainer');
        const slides = carousel.querySelectorAll('.carousel-slide');
        const indicators = carousel.querySelectorAll('.carousel-indicator');
        const prevBtn = carousel.querySelector('.carousel-control.prev');
        const nextBtn = carousel.querySelector('.carousel-control.next');
        
        let currentIndex = 0;
        
        function updateCarousel() {
            if (slides.length === 0) return;
            
            const slideWidth = slides[0].offsetWidth;
            container.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
            
            // Actualizar indicadores
            indicators.forEach((indicator, index) => {
                if (index === currentIndex) {
                    indicator.classList.add('active');
                } else {
                    indicator.classList.remove('active');
                }
            });
            
            // Actualizar slides
            slides.forEach((slide, index) => {
                if (index === currentIndex) {
                    slide.classList.add('active');
                } else {
                    slide.classList.remove('active');
                }
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                currentIndex = (currentIndex - 1 + slides.length) % slides.length;
                updateCarousel();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                currentIndex = (currentIndex + 1) % slides.length;
                updateCarousel();
            });
        }
        
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                currentIndex = index;
                updateCarousel();
            });
        });
        
        // Auto-play
        let interval = setInterval(() => {
            if (slides.length > 0) {
                currentIndex = (currentIndex + 1) % slides.length;
                updateCarousel();
            }
        }, 5000);
        
        carousel.addEventListener('mouseenter', () => clearInterval(interval));
        carousel.addEventListener('mouseleave', () => {
            interval = setInterval(() => {
                if (slides.length > 0) {
                    currentIndex = (currentIndex + 1) % slides.length;
                    updateCarousel();
                }
            }, 5000);
        });
        
        // Inicializar
        updateCarousel();
        
        // Recalcular en resize
        window.addEventListener('resize', updateCarousel);
    }
    
    // Slider básico
    const slider = document.querySelector('.trabajadores-slider');
    if (slider) {
        const container = document.getElementById('trabajadoresContainer');
        const cards = slider.querySelectorAll('.trabajador-card');
        const prevBtn = slider.querySelector('.slider-control.prev');
        const nextBtn = slider.querySelector('.slider-control.next');
        
        if (cards.length === 0) return;
        
        let currentIndex = 0;
        const cardWidth = cards[0].offsetWidth + 20; // 20px de gap
        const visibleCards = Math.floor(slider.offsetWidth / cardWidth);
        const maxIndex = Math.max(0, cards.length - visibleCards);
        
        function updateSlider() {
            container.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
            
            // Actualizar botones
            if (prevBtn) {
                prevBtn.style.opacity = currentIndex > 0 ? '1' : '0.5';
                prevBtn.disabled = currentIndex <= 0;
            }
            
            if (nextBtn) {
                nextBtn.style.opacity = currentIndex < maxIndex ? '1' : '0.5';
                nextBtn.disabled = currentIndex >= maxIndex;
            }
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateSlider();
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentIndex < maxIndex) {
                    currentIndex++;
                    updateSlider();
                }
            });
        }
        
        // Inicializar
        updateSlider();
        
        // Recalcular en resize
        window.addEventListener('resize', () => {
            const newVisibleCards = Math.floor(slider.offsetWidth / cardWidth);
            const newMaxIndex = Math.max(0, cards.length - newVisibleCards);
            if (currentIndex > newMaxIndex) {
                currentIndex = newMaxIndex;
            }
            updateSlider();
        });
    }
}

// Hacer disponible globalmente
if (typeof window !== 'undefined') {
    window.initMuseoEffects = initMuseoEffects;
}

function initObjetosSlider() {
    const objetosContainer = document.getElementById('objetosContainer');
    const prevBtn = document.querySelector('#objetos .slider-control.prev');
    const nextBtn = document.querySelector('#objetos .slider-control.next');
    
    if (!objetosContainer || !prevBtn || !nextBtn) return;
    
    const cardWidth = 320; // Ancho de cada card + gap
    const scrollAmount = cardWidth * 2; // Desplazar 2 cards
    
    prevBtn.addEventListener('click', () => {
        objetosContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
    
    nextBtn.addEventListener('click', () => {
        objetosContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
    
    // Actualizar visibilidad de botones según scroll
    objetosContainer.addEventListener('scroll', () => {
        const maxScroll = objetosContainer.scrollWidth - objetosContainer.clientWidth;
        prevBtn.disabled = objetosContainer.scrollLeft <= 0;
        nextBtn.disabled = objetosContainer.scrollLeft >= maxScroll;
    });
    
    // Inicializar estado de botones
    const maxScroll = objetosContainer.scrollWidth - objetosContainer.clientWidth;
    prevBtn.disabled = true;
    nextBtn.disabled = objetosContainer.scrollWidth <= objetosContainer.clientWidth;
}

// Función genérica para sliders
function initSlider(containerId, sectionClass) {
    const container = document.getElementById(containerId);
    const prevBtn = document.querySelector(`.${sectionClass} .slider-control.prev`);
    const nextBtn = document.querySelector(`.${sectionClass} .slider-control.next`);
    
    if (!container || !prevBtn || !nextBtn) return;
    
    const cardWidth = 320;
    const scrollAmount = cardWidth * 2;
    
    prevBtn.addEventListener('click', () => {
        container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
    
    nextBtn.addEventListener('click', () => {
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
    
    container.addEventListener('scroll', () => {
        const maxScroll = container.scrollWidth - container.clientWidth;
        prevBtn.disabled = container.scrollLeft <= 0;
        nextBtn.disabled = container.scrollLeft >= maxScroll;
    });
    
    const maxScroll = container.scrollWidth - container.clientWidth;
    prevBtn.disabled = true;
    nextBtn.disabled = container.scrollWidth <= container.clientWidth;
}

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    if (typeof initMuseoEffects === 'function') {
        initMuseoEffects();
    }

    initObjetosSlider();
    
    // También puedes reutilizar la función si ya tienes slider
    initSlider('objetosContainer', 'objetos');
});