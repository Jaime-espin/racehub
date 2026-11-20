/**
 * RaceHub - Frontend Application Logic
 * Modular, mantenible y sin dependencias externas.
 */

let carrerasCache = [];
let vistaActual = 'tabla';
let filtroPlanificacion = 'todas';
let usuarioActual = { nombre: '', email: '' };
let carreraGestion = null;
let datosEncontrados = null;

// ==========================================
// Inicializacion
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Cierre al pulsar fuera de los modales
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) cerrarModal(overlay.id);
        });
    });

    cargarCarreras();
});

// ==========================================
// Control de Modales
// ==========================================

function abrirModal(id) {
    const el = document.getElementById(id);
    if (el) el.removeAttribute('hidden');
}

function cerrarModal(id) {
    const el = document.getElementById(id);
    if (el) el.setAttribute('hidden', '');
}

// ==========================================
// Carga de Datos y API
// ==========================================

async function cargarCarreras() {
    try {
        const res = await fetch('/carreras', { credentials: 'include' });
        if (res.status === 401) {
            document.getElementById('btnLogin').style.display = 'inline-flex';
            document.getElementById('btnPerfil').style.display = 'none';
            document.getElementById('btnShare').style.display = 'none';
            document.getElementById('btnLogout').style.display = 'none';
            abrirModal('modalLogin');
            return;
        }

        document.getElementById('btnLogin').style.display = 'none';
        document.getElementById('btnPerfil').style.display = 'inline-flex';
        document.getElementById('btnShare').style.display = 'inline-flex';
        document.getElementById('btnLogout').style.display = 'inline-flex';

        carrerasCache = await res.json();
        cargarPerfil();
        renderizarCarreras();
    } catch (err) {
        console.error('Error cargando carreras:', err);
    }
}

// ==========================================
// Autenticacion y Perfil
// ==========================================

async function login() {
    const email = document.getElementById('loginEmail').value.trim();
    const errorEl = document.getElementById('loginError');

    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email })
        });

        if (res.ok) {
            cerrarModal('modalLogin');
            errorEl.style.display = 'none';
            cargarCarreras();
        } else {
            const data = await res.json();
            errorEl.textContent = data.detail || 'Error al iniciar sesion';
            errorEl.style.display = 'block';
        }
    } catch (err) {
        errorEl.textContent = 'Error de conexion: ' + err.message;
        errorEl.style.display = 'block';
    }
}

async function logout() {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' });
    location.reload();
}

async function cargarPerfil() {
    try {
        const res = await fetch('/perfil', { credentials: 'include' });
        if (res.ok) {
            usuarioActual = await res.json();
        }
    } catch (err) {
        console.error('Error cargando perfil:', err);
    }
}

function abrirPerfil() {
    document.getElementById('perfilNombre').value = usuarioActual.nombre || '';
    abrirModal('modalPerfil');
}

async function guardarPerfil() {
    const nuevoNombre = document.getElementById('perfilNombre').value.trim();
    if (!nuevoNombre) return alert('El nombre no puede estar vacio');

    try {
        const res = await fetch('/perfil', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ nombre_completo: nuevoNombre })
        });
        if (res.ok) {
            usuarioActual.nombre = nuevoNombre;
            cerrarModal('modalPerfil');
            if (carreraGestion) {
                document.getElementById('resModalCorredor').textContent = nuevoNombre;
            }
        }
    } catch (err) {
        alert('Error al guardar perfil: ' + err);
    }
}

async function compartirCalendario() {
    try {
        const res = await fetch('/share/token', { credentials: 'include' });
        const data = await res.json();
        const fullUrl = window.location.origin + data.share_url;
        document.getElementById('shareUrlInput').value = fullUrl;
        abrirModal('modalCompartir');
    } catch (err) {
        alert('Error al generar enlace: ' + err);
    }
}

function copiarEnlace(e) {
    const input = document.getElementById('shareUrlInput');
    input.select();
    navigator.clipboard.writeText(input.value);
    const btn = e.target;
    const oldText = btn.textContent;
    btn.textContent = 'Copiado';
    setTimeout(() => btn.textContent = oldText, 2000);
}

// ==========================================
// Vistas y Filtros
// ==========================================

function cambiarVista(vista) {
    vistaActual = vista;
    document.getElementById('btnTabla').classList.toggle('active', vista === 'tabla');
    document.getElementById('btnCalendario').classList.toggle('active', vista === 'calendario');
    renderizarCarreras();
}

function setFiltroPlanificacion(filtro) {
    filtroPlanificacion = filtro;
    document.querySelectorAll('.plan-filter').forEach(btn => {
        const label = btn.textContent.toLowerCase();
        btn.classList.toggle('active', filtro === 'todas' ? label === 'todas' : label.includes(filtro));
    });
    renderizarCarreras();
}

function normalizarPlan(estado) {
    const validos = ['candidata', 'seleccionada', 'inscrita', 'descartada'];
    const s = (estado || 'candidata').toLowerCase().trim();
    return validos.includes(s) ? s : 'candidata';
}

function renderPlanBadge(plan, enColision) {
    const nombres = { candidata: 'Candidata', seleccionada: 'Seleccionada', inscrita: 'Inscrita', descartada: 'Descartada' };
    const html = `<span class="badge-plan plan-${plan}">${nombres[plan] || 'Candidata'}</span>`;
    return enColision ? `${html} <span class="badge-colision" title="Misma fecha que otra carrera seleccionada">Colision</span>` : html;
}

// ==========================================
// Busqueda con IA y Alta de Carrera
// ==========================================

async function buscarCarrera() {
    const input = document.getElementById('nombreInput');
    const btn = document.getElementById('btnBuscar');
    const loading = document.getElementById('loading');
    const confirmBox = document.getElementById('confirmacion');
    const nombre = input.value.trim();

    if (!nombre) return alert('Escribe el nombre de la carrera');

    confirmBox.style.display = 'none';
    btn.disabled = true;
    loading.style.display = 'block';

    try {
        const res = await fetch('/carreras/buscar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre })
        });

        if (res.ok) {
            datosEncontrados = await res.json();
            const dep = (datosEncontrados.deporte || '').toLowerCase();
            const est = (datosEncontrados.estado_inscripcion || 'pendiente').toLowerCase();
            confirmBox.innerHTML = `
                <h3 style="margin-bottom:12px;">Carrera encontrada por la IA (puedes ajustar cualquier dato antes de guardar)</h3>
                <div class="confirm-grid">
                    <div class="form-group">
                        <label>Nombre oficial</label>
                        <input type="text" id="confirm_nombre" value="${datosEncontrados.nombre_oficial}">
                    </div>
                    <div class="form-group">
                        <label>Fecha</label>
                        <input type="date" id="confirm_fecha" value="${datosEncontrados.fecha}">
                    </div>
                    <div class="form-group">
                        <label>Deporte</label>
                        <select id="confirm_deporte">
                            <option value="Trail" ${dep === 'trail' ? 'selected' : ''}>Trail</option>
                            <option value="Running" ${dep === 'running' ? 'selected' : ''}>Running</option>
                            <option value="Ciclismo" ${dep === 'ciclismo' ? 'selected' : ''}>Ciclismo</option>
                            <option value="Gravel" ${dep === 'gravel' ? 'selected' : ''}>Gravel</option>
                            <option value="Triatlon" ${dep.includes('triatl') ? 'selected' : ''}>Triatlon</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Lugar</label>
                        <input type="text" id="confirm_lugar" value="${datosEncontrados.lugar || ''}">
                    </div>
                    <div class="form-group">
                        <label>Distancias (separadas por comas)</label>
                        <input type="text" id="confirm_distancias" value="${(datosEncontrados.distancias || []).join(', ')}">
                    </div>
                    <div class="form-group">
                        <label>Estado inscripcion</label>
                        <select id="confirm_estado">
                            <option value="abierta" ${est === 'abierta' ? 'selected' : ''}>Abierta</option>
                            <option value="cerrada" ${est === 'cerrada' ? 'selected' : ''}>Cerrada</option>
                            <option value="pendiente" ${est === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                        </select>
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Web oficial</label>
                        <input type="url" id="confirm_url" value="${datosEncontrados.url_oficial || ''}">
                    </div>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-primary" onclick="confirmarGuardado()">Confirmar y Guardar</button>
                    <button class="btn btn-secondary" onclick="cancelarBusqueda()">Cancelar</button>
                </div>
            `;
            confirmBox.style.display = 'block';
            input.value = '';
        } else {
            const err = await res.json();
            alert('Error: ' + (err.detail || 'No se pudo encontrar la carrera'));
        }
    } catch (err) {
        alert('Error de conexion: ' + err.message);
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

async function confirmarGuardado() {
    if (!datosEncontrados) return;

    const payload = {
        nombre_oficial: document.getElementById('confirm_nombre')?.value.trim() || datosEncontrados.nombre_oficial,
        deporte: document.getElementById('confirm_deporte')?.value || datosEncontrados.deporte,
        fecha: document.getElementById('confirm_fecha')?.value || datosEncontrados.fecha,
        lugar: document.getElementById('confirm_lugar')?.value.trim() || datosEncontrados.lugar,
        distancias: (document.getElementById('confirm_distancias')?.value || '')
            .split(',')
            .map(s => s.trim())
            .filter(Boolean),
        estado_inscripcion: document.getElementById('confirm_estado')?.value || datosEncontrados.estado_inscripcion,
        url_oficial: document.getElementById('confirm_url')?.value.trim() || datosEncontrados.url_oficial || null
    };

    if (!payload.distancias.length && datosEncontrados.distancias) {
        payload.distancias = datosEncontrados.distancias;
    }

    try {
        const res = await fetch('/carreras/confirmar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            document.getElementById('confirmacion').style.display = 'none';
            datosEncontrados = null;
            cargarCarreras();
        } else {
            const err = await res.json();
            alert('Error al guardar: ' + (err.detail || 'Error desconocido'));
        }
    } catch (err) {
        alert('Error de conexion: ' + err.message);
    }
}

function cancelarBusqueda() {
    document.getElementById('confirmacion').style.display = 'none';
    datosEncontrados = null;
}

// ==========================================
// Acciones de Carrera
// ==========================================

async function actualizarEstadoPlanificacion(carreraId, estado) {
    try {
        const res = await fetch(`/carreras/${carreraId}/estado`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ estado })
        });
        if (res.ok) cargarCarreras();
        else alert('No se pudo actualizar el estado');
    } catch (err) {
        alert('Error: ' + err);
    }
}

async function marcarInscrita(carreraId) {
    try {
        const res = await fetch(`/carreras/${carreraId}/inscripcion`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({})
        });
        if (res.ok) cargarCarreras();
        else alert('No se pudo marcar la inscripcion');
    } catch (err) {
        alert('Error: ' + err);
    }
}

async function eliminarCarrera(id, nombre) {
    if (!confirm(`Seguro que deseas eliminar "${nombre}"?`)) return;
    try {
        const res = await fetch(`/carreras/${id}`, { method: 'DELETE', credentials: 'include' });
        if (res.ok) cargarCarreras();
        else alert('No se pudo eliminar');
    } catch (err) {
        alert('Error: ' + err);
    }
}

// ==========================================
// Gestion Unificada de Resultados
// ==========================================

function abrirGestionResultado(carreraId) {
    carreraGestion = carrerasCache.find(c => c.id === carreraId);
    if (!carreraGestion) return;

    const fechaCarrera = new Date(carreraGestion.fecha);
    const anio = fechaCarrera.getFullYear() || new Date().getFullYear();

    document.getElementById('resModalTitulo').textContent = `${carreraGestion.nombre} (${anio})`;
    document.getElementById('resModalCorredor').textContent = usuarioActual.nombre || 'Sin configurar';
    document.getElementById('inputUrlOficial').value = carreraGestion.url_oficial || '';

    const resGuardado = carreraGestion.resultados?.[0];
    const tieneResultado = resGuardado && resGuardado.tiempo_oficial;

    const existentePanel = document.getElementById('resExistentePanel');
    const tabsPanel = document.getElementById('resTabsPanel');
    const msgEstado = document.getElementById('resMensajeEstado');
    msgEstado.style.display = 'none';

    if (tieneResultado) {
        document.getElementById('resViewTiempo').textContent = resGuardado.tiempo_oficial;
        document.getElementById('resViewPos').textContent = resGuardado.posicion_general || '--';
        document.getElementById('resViewCat').textContent = resGuardado.posicion_categoria || '--';
        document.getElementById('resViewRitmo').textContent = resGuardado.ritmo_medio || '--';
        existentePanel.style.display = 'block';
        tabsPanel.style.display = 'none';
    } else {
        existentePanel.style.display = 'none';
        tabsPanel.style.display = 'block';
        activarTabResultado('web');
    }

    abrirModal('modalResultado');
}

function mostrarTabsResultado(mostrar) {
    document.getElementById('resExistentePanel').style.display = mostrar ? 'none' : 'block';
    document.getElementById('resTabsPanel').style.display = mostrar ? 'block' : 'none';
    if (mostrar) activarTabResultado('web');
}

function activarTabResultado(tab) {
    document.getElementById('tabBtnWeb').classList.toggle('active', tab === 'web');
    document.getElementById('tabBtnArchivo').classList.toggle('active', tab === 'archivo');
    document.getElementById('tabBtnManual').classList.toggle('active', tab === 'manual');

    document.getElementById('tabPanelWeb').classList.toggle('active', tab === 'web');
    document.getElementById('tabPanelArchivo').classList.toggle('active', tab === 'archivo');
    document.getElementById('tabPanelManual').classList.toggle('active', tab === 'manual');
}

function mostrarMensajeResultado(texto, esError = false) {
    const el = document.getElementById('resMensajeEstado');
    el.textContent = texto;
    el.style.display = 'block';
    el.style.background = esError ? 'var(--danger-light)' : 'var(--success-light)';
    el.style.color = esError ? 'var(--danger)' : 'var(--success)';
}

async function ejecutarBusquedaWeb() {
    if (!carreraGestion) return;
    const url = document.getElementById('inputUrlOficial').value.trim();
    const anio = new Date(carreraGestion.fecha).getFullYear() || new Date().getFullYear();

    mostrarMensajeResultado('Buscando con IA en portales oficiales y clasificaciones...');

    try {
        const res = await fetch('/resultados/buscar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                nombre_carrera: carreraGestion.nombre,
                anio: anio,
                nombre_corredor: usuarioActual.nombre || null,
                url_oficial: url || carreraGestion.url_oficial || null
            })
        });

        const data = await res.json();
        if (data.encontrado) {
            mostrarMensajeResultado(`Resultado encontrado: Tiempo ${data.tiempo}, Posicion #${data.posicion}`);
            cargarCarreras().then(() => abrirGestionResultado(carreraGestion.id));
        } else {
            mostrarMensajeResultado('No se encontro automaticamente. Puedes subir el archivo de resultados o ingresarlo manualmente.', true);
        }
    } catch (err) {
        mostrarMensajeResultado('Error de conexion: ' + err.message, true);
    }
}

async function ejecutarSubidaArchivo() {
    if (!carreraGestion) return;
    const fileInput = document.getElementById('inputArchivo');
    const archivo = fileInput.files?.[0];
    if (!archivo) return alert('Selecciona un archivo PDF o CSV');

    const anio = new Date(carreraGestion.fecha).getFullYear() || new Date().getFullYear();
    const formData = new FormData();
    formData.append('file', archivo);
    formData.append('nombre_carrera', carreraGestion.nombre);
    formData.append('nombre_corredor', usuarioActual.nombre || '');
    formData.append('anio', anio);

    mostrarMensajeResultado('Procesando archivo de clasificaciones con IA...');

    try {
        const res = await fetch('/resultados/buscar-archivo', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });

        const data = await res.json();
        if (data.encontrado) {
            mostrarMensajeResultado(`Resultado extraido del archivo: Tiempo ${data.tiempo}, Posicion #${data.posicion}`);
            fileInput.value = '';
            cargarCarreras().then(() => abrirGestionResultado(carreraGestion.id));
        } else {
            mostrarMensajeResultado(`No se encontro a "${usuarioActual.nombre}" en el documento subido.`, true);
        }
    } catch (err) {
        mostrarMensajeResultado('Error: ' + err.message, true);
    }
}

async function guardarResultadoManual() {
    if (!carreraGestion) return;
    const tiempo = document.getElementById('manTiempo').value.trim();
    const pos = document.getElementById('manPos').value.trim();
    const cat = document.getElementById('manCat').value.trim();
    const ritmo = document.getElementById('manRitmo').value.trim();

    if (!tiempo || !pos) return alert('Completa al menos el tiempo y posicion');
    if (!/^\d{1,2}:\d{2}:\d{2}$/.test(tiempo)) return alert('Formato de tiempo invalido. Usa HH:MM:SS (ej: 01:45:30)');

    const anio = new Date(carreraGestion.fecha).getFullYear() || new Date().getFullYear();

    try {
        const res = await fetch('/resultados/manual', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                nombre_carrera: carreraGestion.nombre,
                anio: anio,
                tiempo_oficial: tiempo,
                posicion_general: parseInt(pos),
                posicion_categoria: cat ? parseInt(cat) : null,
                ritmo_medio: ritmo || null
            })
        });

        if (res.ok) {
            mostrarMensajeResultado('Resultado guardado correctamente');
            cargarCarreras().then(() => abrirGestionResultado(carreraGestion.id));
        } else {
            const err = await res.json();
            mostrarMensajeResultado('Error: ' + (err.detail || 'No se pudo guardar'), true);
        }
    } catch (err) {
        mostrarMensajeResultado('Error: ' + err.message, true);
    }
}

async function eliminarResultadoActual() {
    if (!carreraGestion || !confirm('Eliminar este resultado guardado?')) return;
    try {
        const res = await fetch(`/resultados/${carreraGestion.id}`, { method: 'DELETE', credentials: 'include' });
        if (res.ok) {
            cargarCarreras().then(() => abrirGestionResultado(carreraGestion.id));
        } else {
            alert('No se pudo eliminar el resultado');
        }
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

function toggleResultadoFila(id) {
    const el = document.getElementById(`row-res-${id}`);
    if (el) {
        el.style.display = el.style.display === 'none' ? 'table-row' : 'none';
    }
}

// ==========================================
// Renderizado: Tabla y Calendario
// ==========================================

function renderizarCarreras() {
    const container = document.getElementById('lista-carreras');

    const filtradas = filtroPlanificacion === 'todas'
        ? carrerasCache
        : carrerasCache.filter(c => normalizarPlan(c.estado_planificacion) === filtroPlanificacion);

    if (!filtradas || filtradas.length === 0) {
        container.innerHTML = '<div class="empty-state">No hay carreras registradas para este filtro.</div>';
        return;
    }

    filtradas.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

    if (vistaActual === 'tabla') {
        renderizarTabla(filtradas, container);
    } else {
        renderizarCalendario(filtradas, container);
    }
}

function renderizarTabla(carreras, container) {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    let rowsHtml = '';

    carreras.forEach(c => {
        const fecha = new Date(c.fecha);
        const esPasada = fecha < hoy;
        const plan = normalizarPlan(c.estado_planificacion);
        const planBadge = renderPlanBadge(plan, c.en_colision);
        const res = c.resultados?.[0];
        const tieneRes = Boolean(res && res.tiempo_oficial);

        let estadoBadge = `<span class="badge badge-${c.estado_inscripcion || 'pendiente'}">${c.estado_inscripcion || 'Pendiente'}</span>`;
        if (esPasada) {
            estadoBadge = `<span class="badge badge-finalizada">Finalizada</span>`;
        }

        const btnInscribir = plan === 'seleccionada' ? `
            <button class="btn btn-secondary" style="font-size:12px; padding:4px 8px; color:var(--success);" onclick="marcarInscrita(${c.id})" title="Marcar como inscrita">Inscribir</button>
        ` : '';

        let btnResultado = '';
        if (esPasada) {
            btnResultado = tieneRes
                ? `<button class="btn btn-secondary" style="font-size:12px; padding:4px 8px;" onclick="toggleResultadoFila(${c.id})" title="Ver marca inline">Marca</button>
                   <button class="btn btn-secondary" style="font-size:12px; padding:4px 8px;" onclick="abrirGestionResultado(${c.id})" title="Gestionar resultado">Resultado</button>`
                : `<button class="btn btn-secondary" style="font-size:12px; padding:4px 8px;" onclick="abrirGestionResultado(${c.id})" title="Anadir resultado">+ Marca</button>`;
        }

        rowsHtml += `
            <tr>
                <td><strong>${c.fecha}</strong></td>
                <td>
                    <div class="race-title">${c.nombre}</div>
                    <div class="race-subtitle">${c.distancia_resumen || ''}</div>
                </td>
                <td>${c.deporte}</td>
                <td>${c.localizacion || '-'}</td>
                <td>${estadoBadge}</td>
                <td>${planBadge}</td>
                <td>
                    <div class="table-actions">
                        <select class="select-estado" onchange="actualizarEstadoPlanificacion(${c.id}, this.value)">
                            <option value="candidata" ${plan === 'candidata' ? 'selected' : ''}>Candidata</option>
                            <option value="seleccionada" ${plan === 'seleccionada' ? 'selected' : ''}>Seleccionada</option>
                            <option value="inscrita" ${plan === 'inscrita' ? 'selected' : ''}>Inscrita</option>
                            <option value="descartada" ${plan === 'descartada' ? 'selected' : ''}>Descartada</option>
                        </select>
                        ${btnInscribir}
                        ${btnResultado}
                        <button class="btn btn-secondary" style="font-size:12px; padding:4px 8px;" onclick="abrirEditarCarrera(${c.id})" title="Editar datos">Editar</button>
                        <button class="btn btn-danger" style="font-size:12px; padding:4px 8px;" onclick="eliminarCarrera(${c.id}, '${c.nombre.replace(/'/g, "\\'")}')" title="Eliminar carrera">Eliminar</button>
                    </div>
                </td>
            </tr>
        `;

        if (esPasada && tieneRes) {
            rowsHtml += `
                <tr id="row-res-${c.id}" class="row-result" style="display:none;">
                    <td colspan="7">
                        <div class="result-card-inline">
                            <div class="result-stats">
                                <div class="stat-item"><span>Tiempo Oficial</span><strong>${res.tiempo_oficial}</strong></div>
                                <div class="stat-item"><span>Posicion General</span><strong>#${res.posicion_general || '--'}</strong></div>
                                <div class="stat-item"><span>Pos. Categoria</span><strong>${res.posicion_categoria ? '#' + res.posicion_categoria : '--'}</strong></div>
                                <div class="stat-item"><span>Ritmo Medio</span><strong>${res.ritmo_medio || '--'}</strong></div>
                                ${res.confianza ? `<div class="stat-item"><span>Confianza</span><strong>${res.confianza}%</strong></div>` : ''}
                            </div>
                            <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="abrirGestionResultado(${c.id})">Editar / Borrar</button>
                        </div>
                    </td>
                </tr>
            `;
        }
    });

    container.innerHTML = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Carrera</th>
                        <th>Deporte</th>
                        <th>Lugar</th>
                        <th>Estado</th>
                        <th>Plan</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>${rowsHtml}</tbody>
            </table>
        </div>
    `;
}

function renderizarCalendario(carreras, container) {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    const agrupadas = {};
    carreras.forEach(c => {
        const d = new Date(c.fecha);
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        if (!agrupadas[key]) agrupadas[key] = [];
        agrupadas[key].push(c);
    });

    let html = '<div class="calendar-view">';

    Object.keys(agrupadas).sort().forEach(key => {
        const [ano, mes] = key.split('-');
        const mesNombre = new Date(ano, mes - 1).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
        const titulo = mesNombre.charAt(0).toUpperCase() + mesNombre.slice(1);

        html += `<div class="month-group"><h3>${titulo}</h3><div class="cards-grid">`;

        agrupadas[key].forEach(c => {
            const fecha = new Date(c.fecha);
            const esPasada = fecha < hoy;
            const dia = fecha.getDate();
            const diaSemana = fecha.toLocaleDateString('es-ES', { weekday: 'short' });
            const plan = normalizarPlan(c.estado_planificacion);
            const planBadge = renderPlanBadge(plan, c.en_colision);
            const res = c.resultados?.[0];
            const tieneRes = Boolean(res && res.tiempo_oficial);

            let resSnippet = '';
            if (esPasada) {
                if (tieneRes) {
                    resSnippet = `<div style="font-size:12px; color:var(--primary); margin-top:4px;">Tiempo: ${res.tiempo_oficial} (Pos. #${res.posicion_general || '--'})</div>`;
                } else {
                    resSnippet = `<button class="btn btn-secondary" style="font-size:11px; padding:3px 8px; margin-top:4px;" onclick="abrirGestionResultado(${c.id})">+ Anadir resultado</button>`;
                }
            }

            html += `
                <div class="calendar-card" style="${esPasada ? 'opacity:0.85; background:#fbfcfe;' : ''}">
                    <div class="calendar-date-badge">
                        <div class="day">${dia}</div>
                        <div class="weekday">${diaSemana}</div>
                    </div>
                    <div class="calendar-card-info">
                        <div class="race-title">${c.nombre}</div>
                        <div class="race-subtitle">${c.deporte}${c.distancia_resumen ? ' • ' + c.distancia_resumen : ''} • ${c.localizacion || '-'}</div>
                        <div style="margin-top:6px; display:flex; gap:6px; align-items:center;">
                            ${planBadge}
                            <span class="badge badge-${esPasada ? 'finalizada' : (c.estado_inscripcion || 'pendiente')}">${esPasada ? 'Finalizada' : (c.estado_inscripcion || 'Pendiente')}</span>
                        </div>
                        ${resSnippet}
                    </div>
                    <div class="calendar-card-actions">
                        <select class="select-estado" onchange="actualizarEstadoPlanificacion(${c.id}, this.value)">
                            <option value="candidata" ${plan === 'candidata' ? 'selected' : ''}>Candidata</option>
                            <option value="seleccionada" ${plan === 'seleccionada' ? 'selected' : ''}>Seleccionada</option>
                            <option value="inscrita" ${plan === 'inscrita' ? 'selected' : ''}>Inscrita</option>
                            <option value="descartada" ${plan === 'descartada' ? 'selected' : ''}>Descartada</option>
                        </select>
                        ${esPasada && tieneRes ? `<button class="btn btn-secondary" style="font-size:11px; padding:4px 8px;" onclick="abrirGestionResultado(${c.id})" title="Gestionar resultado">Resultado</button>` : ''}
                        <button class="btn btn-secondary" style="font-size:11px; padding:4px 8px;" onclick="abrirEditarCarrera(${c.id})" title="Editar datos">Editar</button>
                        <button class="btn btn-danger" style="font-size:11px; padding:4px 8px;" onclick="eliminarCarrera(${c.id}, '${c.nombre.replace(/'/g, "\\'")}')" title="Eliminar carrera">Eliminar</button>
                    </div>
                </div>
            `;
        });

        html += '</div></div>';
    });

    html += '</div>';
    container.innerHTML = html;
}

// ==========================================
// Edicion Directa de Carreras
// ==========================================

function abrirEditarCarrera(id) {
    const c = carrerasCache.find(item => item.id === id);
    if (!c) return;
    document.getElementById('edit_carrera_id').value = c.id;
    document.getElementById('edit_nombre').value = c.nombre;
    document.getElementById('edit_fecha').value = c.fecha;
    document.getElementById('edit_deporte').value = c.deporte;
    document.getElementById('edit_lugar').value = c.localizacion || '';
    document.getElementById('edit_distancias').value = c.distancia_resumen || '';
    document.getElementById('edit_url').value = c.url_oficial || '';
    abrirModal('modalEditarCarrera');
}

async function guardarEdicionCarrera() {
    const id = document.getElementById('edit_carrera_id').value;
    const payload = {
        nombre: document.getElementById('edit_nombre').value.trim(),
        fecha: document.getElementById('edit_fecha').value,
        deporte: document.getElementById('edit_deporte').value,
        localizacion: document.getElementById('edit_lugar').value.trim(),
        distancia_resumen: document.getElementById('edit_distancias').value.trim(),
        url_oficial: document.getElementById('edit_url').value.trim()
    };

    try {
        const res = await fetch(`/carreras/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            cerrarModal('modalEditarCarrera');
            cargarCarreras();
        } else {
            const err = await res.json();
            alert('Error al actualizar: ' + (err.detail || 'Fallo desconocido'));
        }
    } catch (err) {
        alert('Error de conexion: ' + err.message);
    }
}
