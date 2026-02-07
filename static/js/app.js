// Inicializar fancybox para la galería
Fancybox.bind("[data-fancybox]", {
});

// Inicializar carrusel y slider
document.addEventListener('DOMContentLoaded', function () {
    // Inicializar las pestañas manualmente
    var tabEls = document.querySelectorAll('#museoTabs a[data-bs-toggle="tab"]');

    tabEls.forEach(function (tabEl) {
        tabEl.addEventListener('click', function (e) {
            e.preventDefault();

            // Obtener el target
            var target = this.getAttribute('href');

            // Remover clases activas de todas las pestañas
            $('#museoTabs a').removeClass('active').attr('aria-selected', 'false');

            // Ocultar todos los paneles
            $('.tab-pane').removeClass('show active');

            // Activar la pestaña clickeada
            $(this).addClass('active').attr('aria-selected', 'true');

            // Mostrar el panel correspondiente
            $(target).addClass('show active');
        });
    });

    // Fecha actual
    var currentDate = new Date();
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = currentDate.toLocaleDateString('es-ES', options);
});