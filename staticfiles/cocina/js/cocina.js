document.addEventListener('DOMContentLoaded', function() {
    var kanban = document.getElementById('cocinaKanban');
    if (!kanban) return;

    function actualizarCocina() {
        var url = '/cocina/htmx/ordenes/';
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var colPendiente = document.getElementById('columna-pendiente');
                var colPreparacion = document.getElementById('columna-preparacion');
                var colListo = document.getElementById('columna-listo');
                if (colPendiente) colPendiente.innerHTML = data.pendientes;
                if (colPreparacion) colPreparacion.innerHTML = data.preparacion;
                if (colListo) colListo.innerHTML = data.listos;

                var c1 = document.getElementById('count-pendiente');
                var c2 = document.getElementById('count-preparacion');
                var c3 = document.getElementById('count-listo');
                var pendientesEl = colPendiente ? colPendiente.querySelectorAll('.orden-card').length : 0;
                var preparacionEl = colPreparacion ? colPreparacion.querySelectorAll('.orden-card').length : 0;
                var listosEl = colListo ? colListo.querySelectorAll('.orden-card').length : 0;
                if (c1) c1.textContent = pendientesEl;
                if (c2) c2.textContent = preparacionEl;
                if (c3) c3.textContent = listosEl;

                if (pendientesEl > 0 || preparacionEl > 0) {
                    var titulo = document.querySelector('h1');
                    if (titulo && !titulo.textContent.includes('🔔')) {
                        titulo.textContent = titulo.textContent.replace('Cocina', 'Cocina 🔔');
                    }
                }
            });
    }

    setInterval(actualizarCocina, 10000);
});
