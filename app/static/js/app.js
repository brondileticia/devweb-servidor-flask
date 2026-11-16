/* ============================================================
   PTBDSWS — comportamentos globais (carregado em base.html)

   Tudo aqui funciona por ATRIBUTOS data-* no HTML, então nenhum
   template precisa de <script> próprio. Para usar, basta marcar o HTML:

     <form data-confirmar="Tem certeza?">        → pede confirmação
     <button data-toggle-senha="idDoInput">      → mostra/oculta senha
     <div data-filtro> ... <input data-filtro-input>
         <x data-filtro-item data-texto="...">   → busca instantânea
   ============================================================ */
(function () {
    'use strict';

    // ---------- 1. Confirmação antes de enviar formulários perigosos ----------
    document.querySelectorAll('form[data-confirmar]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm(form.dataset.confirmar)) e.preventDefault();
        });
    });

    // ---------- 2. Mostrar / ocultar senha ----------
    document.querySelectorAll('[data-toggle-senha]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var input = document.getElementById(btn.dataset.toggleSenha);
            var icone = btn.querySelector('i');
            var mostrar = input.type === 'password';
            input.type = mostrar ? 'text' : 'password';
            if (icone) {
                icone.classList.toggle('bi-eye', !mostrar);
                icone.classList.toggle('bi-eye-slash', mostrar);
            }
        });
    });

    // ---------- 3. Busca instantânea (home, paleta e tabela de usuários) ----------

    // "Formulário" e "formulario" devem casar: remove acentos e caixa.
    function normalizar(texto) {
        return (texto || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    }

    function ligarFiltro(raiz) {
        var input = raiz.querySelector('[data-filtro-input]');
        if (!input) return;
        var itens = Array.prototype.slice.call(raiz.querySelectorAll('[data-filtro-item]'));
        var grupos = raiz.querySelectorAll('[data-filtro-grupo]');
        var vazio = raiz.querySelector('[data-filtro-vazio]');

        // Pré-calcula o texto de busca de cada item uma única vez
        itens.forEach(function (item) { item._busca = normalizar(item.dataset.texto); });

        function aplicar() {
            var termos = normalizar(input.value).split(/\s+/).filter(Boolean);
            var visiveis = 0;
            itens.forEach(function (item) {
                // Todos os termos digitados precisam aparecer (busca "E")
                var ok = termos.every(function (t) { return item._busca.indexOf(t) !== -1; });
                item.hidden = !ok;
                if (ok) visiveis++;
            });
            grupos.forEach(function (g) {
                g.hidden = !g.querySelector('[data-filtro-item]:not([hidden])');
            });
            if (vazio) vazio.hidden = visiveis > 0;
        }

        // Itens visíveis que podem receber foco (links)
        function focaveis() {
            return itens.filter(function (i) { return !i.hidden && i.tagName === 'A'; });
        }

        input.addEventListener('input', aplicar);

        // Setas ↑ ↓ navegam; Enter no campo abre o primeiro resultado
        raiz.addEventListener('keydown', function (e) {
            var lista = focaveis();
            if (!lista.length) return;
            var atual = lista.indexOf(document.activeElement);

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                lista[Math.min(atual + 1, lista.length - 1)].focus();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (atual <= 0) input.focus();
                else lista[atual - 1].focus();
            } else if (e.key === 'Enter' && document.activeElement === input) {
                e.preventDefault();
                lista[0].click();
            }
        });

        raiz._limparFiltro = function () { input.value = ''; aplicar(); };
    }

    document.querySelectorAll('[data-filtro]').forEach(ligarFiltro);

    // ---------- 4. Atalhos de teclado ----------
    var paleta = document.getElementById('paleta');

    function digitandoEmCampo(alvo) {
        return alvo && (alvo.tagName === 'INPUT' || alvo.tagName === 'TEXTAREA' ||
                        alvo.tagName === 'SELECT' || alvo.isContentEditable);
    }

    document.addEventListener('keydown', function (e) {
        // Ctrl+K (ou ⌘K no Mac) abre a paleta de comandos
        if (paleta && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            bootstrap.Modal.getOrCreateInstance(paleta).toggle();
            return;
        }
        // "/" foca a busca de atividades da página (se existir)
        if (e.key === '/' && !digitandoEmCampo(e.target)) {
            var busca = document.querySelector('main .launcher [data-filtro-input]');
            if (busca) { e.preventDefault(); busca.focus(); }
        }
    });

    if (paleta) {
        var raizPaleta = paleta.querySelector('[data-filtro]');
        paleta.addEventListener('shown.bs.modal', function () {
            paleta.querySelector('[data-filtro-input]').focus();
        });
        paleta.addEventListener('hidden.bs.modal', function () {
            if (raizPaleta && raizPaleta._limparFiltro) raizPaleta._limparFiltro();
        });
    }
})();
