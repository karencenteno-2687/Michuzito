document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('productoModal');
    if (!modal) return;

    modal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var productoId = button ? button.getAttribute('data-producto-id') : null;
        var card = event.target.closest ? null : null;

        if (!productoId) {
            var cardEl = button ? button.closest('[data-producto-id]') : null;
            if (cardEl) productoId = cardEl.getAttribute('data-producto-id');
        }
    });

    document.querySelectorAll('[data-producto-id]').forEach(function (card) {
        card.addEventListener('click', function (e) {
            if (e.target.closest('a, button, .btn')) return;
            var id = this.getAttribute('data-producto-id');
            if (!id) return;
            var url = '/htmx/producto/' + id + '/';
            var modalEl = document.getElementById('productoModal');
            var modalContent = document.getElementById('modalContent');
            if (!modalEl || !modalContent) return;
            modalContent.innerHTML = '<div class="modal-body text-center py-5"><div class="spinner-border text-warning" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
            var bsModal = new bootstrap.Modal(modalEl);
            bsModal.show();
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                modalContent.innerHTML = data.html;
            })
            .catch(function () {
                modalContent.innerHTML = '<div class="modal-body text-center py-5"><p class="text-danger">Error al cargar el producto.</p></div>';
            });
        });
    });

    document.addEventListener('htmx:afterSwap', function (evt) {
        if (evt.detail.target && evt.detail.target.id === 'productosContainer') {
            document.querySelectorAll('[data-producto-id]').forEach(function (card) {
                card.addEventListener('click', function (e) {
                    if (e.target.closest('a, button, .btn')) return;
                    var id = this.getAttribute('data-producto-id');
                    if (!id) return;
                    var url = '/htmx/producto/' + id + '/';
                    var modalEl = document.getElementById('productoModal');
                    var modalContent = document.getElementById('modalContent');
                    if (!modalEl || !modalContent) return;
                    modalContent.innerHTML = '<div class="modal-body text-center py-5"><div class="spinner-border text-warning" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
                    var bsModal = new bootstrap.Modal(modalEl);
                    bsModal.show();
                    fetch(url, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(function (response) { return response.json(); })
                    .then(function (data) {
                        modalContent.innerHTML = data.html;
                    })
                    .catch(function () {
                        modalContent.innerHTML = '<div class="modal-body text-center py-5"><p class="text-danger">Error al cargar el producto.</p></div>';
                    });
                });
            });
        }
    });

    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });
});
