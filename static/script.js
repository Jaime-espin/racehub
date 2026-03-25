        let datosEncontrados = null;
        let vistaActual = 'tabla'; // 'tabla' o 'calendario'
        let carrerasCache = [];

        console.log("Script loaded");

        // Cerrar menú móvil al hacer click en cualquier botón del menú
        document.addEventListener('DOMContentLoaded', () => {
            const menuButtons = document.querySelectorAll('.menu .btn-nav');
            const menuToggle = document.getElementById('menu-toggle');
            
            menuButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    if (window.innerWidth <= 768) {
                        menuToggle.checked = false;
                    }
                });
            });

            // Ocultar botones de usuario hasta que se confirme login
            document.querySelectorAll('.btn-perfil, .btn-share, .btn-logout').forEach(btn => btn.style.display = 'none');

            // Cargar carreras al iniciar la página
            cargarCarreras();
        });

        function cambiarVista(vista) {
            vistaActual = vista;
            document.getElementById('btnTabla').classList.toggle('active', vista === 'tabla');
            document.getElementById('btnCalendario').classList.toggle('active', vista === 'calendario');
            renderizarCarreras(carrerasCache);
        }

        async function cargarCarreras() {
            try {
                const response = await fetch('/carreras', { credentials: 'include' });
                if (response.status === 401) {
                    document.getElementById('modalLogin').style.display = 'flex';
                    return;
                }
                const carreras = await response.json();
                carrerasCache = carreras;
                renderizarCarreras(carreras);
                
                // Mostrar botones de usuario ya que está logueado
                document.querySelectorAll('.btn-perfil, .btn-share, .btn-logout').forEach(btn => btn.style.display = 'inline-block');
                
                // Ocultar botón de login
                document.getElementById('btnLogin').style.display = 'none';
                
                // Cargar perfil tras cargar carreras (si login ok)
                cargarPerfil();
            } catch (error) {
                console.error("Error al cargar:", error);
            }
        }

        async function login() {
            const email = document.getElementById('loginEmail').value;
            console.log("Login attempt with:", email);
            if (!email || !email.includes('@')) {
                document.getElementById('loginError').textContent = "Email inválido";
                document.getElementById('loginError').style.display = 'block';
                return;
            }
            
            document.getElementById('loginError').style.display = 'none';
            
            try {
                const res = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: email}),
                    credentials: 'include'
                });
                
                if (res.ok) {
                    document.getElementById('modalLogin').style.display = 'none';
                    cargarCarreras();
                } else {
                    const error = await res.json();
                    document.getElementById('loginError').textContent = "Error al entrar: " + (error.detail || "Desconocido");
                    document.getElementById('loginError').style.display = 'block';
                }
            } catch (e) {
                document.getElementById('loginError').textContent = "Error de conexión: " + e.message;
                document.getElementById('loginError').style.display = 'block';
            }
        }

        async function logout() {
            await fetch('/auth/logout', {method: 'POST', credentials: 'include'});
            // Ocultar botones de usuario
            document.querySelectorAll('.btn-perfil, .btn-share, .btn-logout').forEach(btn => btn.style.display = 'none');
            location.reload();
        }

        function renderizarCarreras(carreras) {
            const listaDiv = document.getElementById('lista-carreras');
            
            if (!carreras || carreras.length === 0) {
                listaDiv.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">📭 No se añadió ninguna carrera todavía.</p>';
                return;
            }
            
            carreras.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
            
            if (vistaActual === 'tabla') {
                renderizarTabla(carreras, listaDiv);
            } else {
                renderizarCalendario(carreras, listaDiv);
            }
        }

        function renderizarTabla(carreras, listaDiv) {
            let html = `<table>
                <tr>
                    <th>Fecha</th>
                    <th>Carrera</th>
                    <th>Deporte</th>
                    <th>Lugar</th>
                    <th>Estado</th>
                    <th>Acción</th>
                </tr>`;

            const hoy = new Date();
            hoy.setHours(0,0,0,0);

            carreras.forEach(c => {
                const fechaCarrera = new Date(c.fecha);
                const esPasada = fechaCarrera < hoy;
                
                let estadoHtml = `<span class="badge ${c.estado_inscripcion || 'pendiente'}">${c.estado_inscripcion || 'Pendiente'}</span>`;
                let accionExtra = '';
                let desplegableHtml = '';
                const idDesplegable = `desplegable-${c.id}`;
                const tieneResultado = c.resultados && c.resultados.length > 0;

                if (esPasada) {
                    estadoHtml = `<span class="badge cerrada" style="background-color: #cbd5e1;">Finalizada</span>`;
                    const anio = fechaCarrera.getFullYear();
                    
                    // Botones circulares minimalistas con SVG
                    if (tieneResultado) {
                        accionExtra = `
                            <button onclick="toggleDesplegable('${idDesplegable}')" title="Ver resultado" style="background:#f1f5f9; border:none; width:36px; height:36px; border-radius:50%; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; margin-right:8px; transition:all 0.3s;" onmouseover="this.style.background='#e0e7ff'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='#f1f5f9'; this.style.transform='scale(1)'">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                                    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                                    <path d="M21 3v5h-5"></path>
                                    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                                    <path d="M3 21v-5h5"></path>
                                </svg>
                            </button>
                        `;
                    } else {
                        accionExtra = `
                            <button onclick="gestionResultado(${c.id}, '${c.nombre}', ${anio})" title="Buscar resultado" style="background:#f1f5f9; border:none; width:36px; height:36px; border-radius:50%; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; margin-right:8px; transition:all 0.3s;" onmouseover="this.style.background='#e0e7ff'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='#f1f5f9'; this.style.transform='scale(1)'">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                    <path d="M16 2v4"></path>
                                    <path d="M8 2v4"></path>
                                    <path d="M3 10h18"></path>
                                    <circle cx="8.5" cy="16" r="1.5"></circle>
                                    <circle cx="15.5" cy="16" r="1.5"></circle>
                                    <circle cx="12" cy="19" r="1.5"></circle>
                                </svg>
                            </button>
                        `;
                    }
                }

                html += `<tr>
                    <td>${c.fecha}</td>
                    <td>
                        <strong>${c.nombre}</strong><br>
                        <small style="color:#777">${c.distancia_resumen || ''}</small>
                    </td>
                    <td>${c.deporte}</td>
                    <td>${c.localizacion}</td>
                    <td>${estadoHtml}</td>
                    <td style="display:flex; gap:8px; align-items:center;">
                        ${accionExtra}
                        <button onclick="eliminarCarrera(${c.id}, '${c.nombre}')" title="Eliminar carrera" style="background:#f1f5f9; border:none; width:36px; height:36px; border-radius:50%; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; transition:all 0.3s;" onmouseover="this.style.background='#fee2e2'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='#f1f5f9'; this.style.transform='scale(1)'">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                <line x1="10" y1="11" x2="10" y2="17"></line>
                                <line x1="14" y1="11" x2="14" y2="17"></line>
                            </svg>
                        </button>
                    </td>
                </tr>`;

                // Agregar fila de desplegable si hay resultado
                if (tieneResultado && esPasada) {
                    const res = c.resultados[0];
                    html += `<tr id="${idDesplegable}" class="fila-desplegable" style="display:none;">
                        <td colspan="6">
                            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:20px; margin:10px 0; font-size:14px;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                                    <h3 style="margin:0; color:#1e293b; font-size:16px; font-weight:600;">Resultado Guardado</h3>
                                    <button onclick="toggleDesplegable('${idDesplegable}')" style="background:#f1f5f9; color:#007AFF; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:500; transition:all 0.3s;" onmouseover="this.style.background='#e0e7ff'" onmouseout="this.style.background='#f1f5f9'">Cerrar</button>
                                </div>
                                <div style="color:#1e293b; display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px;">
                                    <div>
                                        <div style="font-size:12px; color:#64748b; font-weight:500; margin-bottom:4px;">Tiempo</div>
                                        <div style="font-weight:600; font-size:18px; color:#007AFF;">${res.tiempo_oficial || '--'}</div>
                                    </div>
                                    <div>
                                        <div style="font-size:12px; color:#64748b; font-weight:500; margin-bottom:4px;">Posición General</div>
                                        <div style="font-weight:600; font-size:18px; color:#007AFF;">${res.posicion_general || '--'}</div>
                                    </div>
                                    <div>
                                        <div style="font-size:12px; color:#64748b; font-weight:500; margin-bottom:4px;">Categoría</div>
                                        <div style="font-weight:600; font-size:18px; color:#007AFF;">${res.posicion_categoria || '--'}</div>
                                    </div>
                                </div>
                                ${res.ritmo_medio ? `<div style="margin-top:15px; padding-top:15px; border-top:1px solid #e2e8f0; color:#1e293b;">
                                    <span style="font-size:12px; color:#64748b; font-weight:500;">Ritmo Medio:</span> <strong style="color:#007AFF; margin-left:5px;">${res.ritmo_medio}</strong>
                                </div>` : ''}
                                ${res.confianza ? `<div style="margin-top:10px; color:#1e293b;"><span style="font-size:12px; color:#64748b; font-weight:500;">Confianza:</span> <strong style="color:#007AFF; margin-left:5px;">${res.confianza}%</strong></div>` : ''}
                                <div style="margin-top:15px; display:flex; gap:10px;">
                                    <button onclick="gestionResultado(${c.id}, '${c.nombre}', ${fechaCarrera.getFullYear()}, true)" style="background:#007AFF; color:white; border:none; padding:8px 14px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:500; transition:all 0.3s;" onmouseover="this.opacity='0.9'" onmouseout="this.opacity='1'">Buscar de nuevo</button>
                                    <button onclick="eliminarResultado(${c.id})" style="background:#f1f5f9; color:#dc2626; border:1px solid #fee2e2; padding:8px 14px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:500; transition:all 0.3s;" onmouseover="this.style.background='#fee2e2'" onmouseout="this.style.background='#f1f5f9'">Borrar</button>
                                </div>
                            </div>
                        </td>
                    </tr>`;
                }
            });
            html += '</table>';
            listaDiv.innerHTML = html;
        }

        function toggleDesplegable(idDesplegable) {
            const fila = document.getElementById(idDesplegable);
            if (fila) {
                const estaOculta = fila.style.display === 'none' || !fila.style.display;
                fila.style.display = estaOculta ? 'table-row' : 'none';
            }
        }

        async function eliminarResultado(carreraId) {
            if (!confirm('¿Borrar este resultado?')) return;
            
            try {
                const response = await fetch(`/resultados/${carreraId}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });
                
                if (response.ok) {
                    cargarCarreras();
                } else {
                    alert('Error al borrar el resultado');
                }
            } catch (error) {
                alert('Error de conexión: ' + error);
            }
        }

        function renderizarCalendario(carreras, listaDiv) {
            // Agrupar carreras por mes
            const carrerasPorMes = {};
            carreras.forEach(c => {
                const fecha = new Date(c.fecha);
                const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
                if (!carrerasPorMes[mesKey]) {
                    carrerasPorMes[mesKey] = [];
                }
                carrerasPorMes[mesKey].push(c);
            });

            const hoy = new Date();
            hoy.setHours(0,0,0,0);

            let html = '<div class="calendario-container">';
            
            Object.keys(carrerasPorMes).sort().forEach(mesKey => {
                const [ano, mes] = mesKey.split('-');
                const nombreMes = new Date(ano, mes - 1).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
                
                html += `<div class="mes-grupo">
                    <h3 class="mes-titulo">${nombreMes.charAt(0).toUpperCase() + nombreMes.slice(1)}</h3>
                    <div class="carreras-mes">`;
                
                carrerasPorMes[mesKey].forEach(c => {
                    const fecha = new Date(c.fecha);
                    const esPasada = fecha < hoy;
                    const dia = fecha.getDate();
                    const diaSemana = fecha.toLocaleDateString('es-ES', { weekday: 'short' });
                    
                    let estadoHtml = `<span class="badge ${c.estado_inscripcion || 'pendiente'}">${c.estado_inscripcion || 'Pendiente'}</span>`;
                    let btnResultado = '';
                    let resultadoHtml = '';

                    if (esPasada) {
                        estadoHtml = `<span class="badge cerrada" style="background-color: #cbd5e1; color: #1e293b;">Finalizada</span>`;
                        const anio = fecha.getFullYear();
                        btnResultado = `<button onclick="gestionResultado(${c.id}, '${c.nombre}', ${anio})" style="margin-top:10px; width:100%; background:#007AFF; color:white; border:none; padding:8px; border-radius:6px; cursor:pointer; font-weight:500; transition:all 0.3s;" onmouseover="this.opacity='0.9'" onmouseout="this.opacity='1'">Ver Resultado</button>`;
                        
                        // Mostrar resultado si existe
                        if (c.resultados && c.resultados.length > 0) {
                            const res = c.resultados[0];
                            resultadoHtml = `
                            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px; margin-top:10px; font-size:13px; color:#1e293b;">
                                <strong style="color:#1e293b; font-size:14px; display:block; margin-bottom:8px;">Resultado Guardado</strong>
                                <div style="margin-top:8px; color:#1e293b; display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;">
                                    <div><span style="color:#64748b; font-size:11px; font-weight:500;">Tiempo</span><div style="font-weight:600; color:#007AFF;">${res.tiempo_oficial || '--'}</div></div>
                                    <div><span style="color:#64748b; font-size:11px; font-weight:500;">Posición</span><div style="font-weight:600; color:#007AFF;">${res.posicion_general || '--'}</div></div>
                                    ${res.posicion_categoria ? `<div><span style="color:#64748b; font-size:11px; font-weight:500;">Categoría</span><div style="font-weight:600; color:#007AFF;">${res.posicion_categoria}</div></div>` : ''}
                                </div>
                            </div>`;
                        }
                    }

                    html += `<div class="carrera-card" style="${esPasada ? 'opacity: 0.85; background: #f8fafc; border: 1px solid #e2e8f0;' : ''}">
                        <div class="carrera-fecha">
                            <div class="dia">${dia}</div>
                            <div class="dia-semana">${diaSemana}</div>
                        </div>
                        <div class="carrera-info">
                            <h4 style="margin-top:0; color:#1e293b;">${c.nombre}</h4>
                            <p style="margin:5px 0; color:#475569; font-size:13px;"><strong>Lugar:</strong> ${c.localizacion}</p>
                            <p style="margin:5px 0; color:#475569; font-size:13px;"><strong>Deporte:</strong> ${c.deporte}${c.distancia_resumen ? ' - ' + c.distancia_resumen : ''}</p>
                            ${estadoHtml}
                            ${btnResultado}
                            ${resultadoHtml}
                        </div>
                        <div class="carrera-acciones">
                            <button onclick="eliminarCarrera(${c.id}, '${c.nombre}')" title="Eliminar carrera" style="background:#f1f5f9; border:none; width:36px; height:36px; border-radius:50%; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; transition:all 0.3s;" onmouseover="this.style.background='#fee2e2'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='#f1f5f9'; this.style.transform='scale(1)'">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    <line x1="10" y1="11" x2="10" y2="17"></line>
                                    <line x1="14" y1="11" x2="14" y2="17"></line>
                                </svg>
                            </button>
                        </div>
                    </div>`;
                });
                
                html += '</div></div>';
            });
            
            html += '</div>';
            listaDiv.innerHTML = html;
        }

        async function buscarCarrera() {
            const input = document.getElementById('nombreInput');
            const btn = document.getElementById('btnBuscar');
            const loading = document.getElementById('loading');
            const confirmacionDiv = document.getElementById('confirmacion');
            const nombre = input.value;

            if (!nombre) return alert("Escribe un nombre primero");

            // Ocultar confirmación previa si existe
            confirmacionDiv.style.display = 'none';

            // Interfaz: Bloqueamos botón y mostramos carga
            btn.disabled = true;
            loading.style.display = 'block';

            try {
                const response = await fetch('/carreras/buscar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre: nombre })
                });

                if (response.ok) {
                    datosEncontrados = await response.json();
                    
                    // Mostrar datos encontrados para confirmación
                    confirmacionDiv.innerHTML = `
                        <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007AFF;">
                            <h3 style="margin-top: 0; color: #1e293b; font-size:16px; font-weight:600;">Datos encontrados</h3>
                            <p style="color:#1e293b; margin:8px 0;"><strong style="color:#475569;">Nombre:</strong> ${datosEncontrados.nombre_oficial}</p>
                            <p style="color:#1e293b; margin:8px 0;"><strong style="color:#475569;">Deporte:</strong> ${datosEncontrados.deporte}</p>
                            <p style="color:#1e293b; margin:8px 0;"><strong style="color:#475569;">Fecha:</strong> ${datosEncontrados.fecha}</p>
                            <p style="color:#1e293b; margin:8px 0;"><strong style="color:#475569;">Lugar:</strong> ${datosEncontrados.lugar}</p>
                            <p style="color:#1e293b; margin:8px 0;"><strong style="color:#475569;">Distancias:</strong> ${datosEncontrados.distancias.join(', ')}</p>
                            <p style="color:#1e293b; margin:8px 0;"><strong style="color:#475569;">URL:</strong> <span style="color:#007AFF; word-break:break-all;">${datosEncontrados.url_oficial || 'No disponible'}</span></p>
                            <p style="color:#1e293b; margin:8px 0;"><strong style="color:#475569;">Estado:</strong> ${datosEncontrados.estado_inscripcion}</p>
                            
                            <div style="margin-top: 20px; display: flex; gap: 10px;">
                                <button onclick="confirmarGuardado()" style="background: #007AFF; color:white; border:none; padding:8px 14px; border-radius:6px; cursor:pointer; font-weight:500; transition:all 0.3s;" onmouseover="this.opacity='0.9'" onmouseout="this.opacity='1'">Confirmar y Guardar</button>
                                <button onclick="cancelarBusqueda()" style="background:#f1f5f9; color:#dc2626; border:1px solid #fee2e2; padding:8px 14px; border-radius:6px; cursor:pointer; font-weight:500; transition:all 0.3s;" onmouseover="this.style.background='#fee2e2'" onmouseout="this.style.background='#f1f5f9'">Cancelar</button>
                            </div>
                        </div>
                    `;
                    confirmacionDiv.style.display = 'block';
                    input.value = ''; // Limpiar input
                } else {
                    const error = await response.json();
                    alert("❌ Error: " + (error.detail || "No se pudo procesar"));
                }
            } catch (err) {
                alert("❌ Error de conexión: " + err);
            } finally {
                // Interfaz: Restauramos estado
                btn.disabled = false;
                loading.style.display = 'none';
            }
        }

        async function confirmarGuardado() {
            if (!datosEncontrados) return;

            try {
                const response = await fetch('/carreras/confirmar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(datosEncontrados)
                });

                if (response.ok) {
                    document.getElementById('confirmacion').style.display = 'none';
                    cargarCarreras();
                    alert("✅ ¡Carrera guardada correctamente!");
                    datosEncontrados = null;
                } else {
                    const error = await response.json();
                    alert("❌ Error al guardar: " + (error.detail || "No se pudo guardar"));
                }
            } catch (err) {
                alert("❌ Error de conexión al guardar");
            }
        }

        function cancelarBusqueda() {
            document.getElementById('confirmacion').style.display = 'none';
            datosEncontrados = null;
            alert("❌ Operación cancelada");
        }

        async function eliminarCarrera(id, nombre) {
            if (!confirm(`¿Estás seguro de eliminar "${nombre}"?`)) {
                return;
            }

            try {
                const response = await fetch(`/carreras/${id}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });

                if (response.ok) {
                    cargarCarreras();
                    alert(`✅ Carrera "${nombre}" eliminada correctamente`);
                } else {
                    const error = await response.json();
                    alert("❌ Error al eliminar: " + (error.detail || "No se pudo eliminar"));
                }
            } catch (err) {
                alert("❌ Error de conexión al eliminar");
            }
        }

        // --- GESTIÓN DE PERFIL ---
        let usuarioActual = { nombre: "" };

        async function cargarPerfil() {
             try {
                const res = await fetch('/perfil', { credentials: 'include' });
                if (res.ok) {
                    usuarioActual = await res.json();
                }
            } catch(e) { console.error("Error cargando perfil", e); }
        }

        function abrirPerfil() {
            if (!usuarioActual) {
                alert("Debes iniciar sesión primero");
                return;
            }
            document.getElementById('perfilNombre').value = usuarioActual.nombre || "";
            document.getElementById('modalPerfil').style.display = 'flex';
        }

        function cerrarPerfil() {
            document.getElementById('modalPerfil').style.display = 'none';
        }

        async function guardarPerfil() {
            const nuevoNombre = document.getElementById('perfilNombre').value;
            if(!nuevoNombre) return alert("El nombre no puede estar vacío");
            
            try {
                const res = await fetch('/perfil', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    credentials: 'include',
                    body: JSON.stringify({ nombre_completo: nuevoNombre })
                });
                if(res.ok) {
                    usuarioActual.nombre = nuevoNombre;
                    cerrarPerfil();
                    alert("✅ Perfil guardado. Ahora las búsquedas usarán este nombre.");
                }
            } catch(e) { alert("Error guardando perfil"); }
        }

        // --- GESTIÓN DE RESULTADOS (VERSIÓN MEJORADA CON MODALES) ---
        let datosResultadoActual = {}; // Almacenar estado durante el flujo

        async function gestionResultado(carreraId, nombreCarrera, anio, forzarBusqueda = false) {
            // 1. Buscar en caché local si ya tenemos el resultado
            const carrera = carrerasCache.find(c => c.id === carreraId);
            const resultadoGuardado = carrera && carrera.resultados && carrera.resultados.length > 0 ? carrera.resultados[0] : null;

            // Si hay resultado guardado Y no estamos forzando búsqueda, mostrarlo
            if (!forzarBusqueda && resultadoGuardado && resultadoGuardado.tiempo_oficial) {
                 // Si ya existe, mostrar con modal personalizado
                 mostrarModalResultadoExistente(resultadoGuardado);
                 return;
            }

            // 2. Guardar información de la búsqueda actual
            datosResultadoActual = {
                nombreCarrera: nombreCarrera,
                anio: anio,
                carreraId: carreraId,
                url_oficial: carrera?.url_oficial
            };

            // 3. Pedir nombre del corredor
            let nombreCorredor = usuarioActual?.nombre;
            
            if (!nombreCorredor) {
                // Mostrar modal para ingresar nombre
                document.getElementById('modalNombreCorredor').style.display = 'flex';
                document.getElementById('nombreCorredorConfirm').textContent = "Introduce tu nombre completo en el perfil primero";
                abrirPerfil();
                return;
            }

            datosResultadoActual.nombreCorredor = nombreCorredor;
            
            // 4. Mostrar modal para confirmar nombre
            document.getElementById('nombreCorredorConfirm').textContent = nombreCorredor;
            document.getElementById('modalNombreCorredor').style.display = 'flex';
        }

        function cerrarModalNombreCorredor() {
            document.getElementById('modalNombreCorredor').style.display = 'none';
        }

        function confirmarNombreCorredor() {
            cerrarModalNombreCorredor();
            // Mostrar modal con opciones de búsqueda
            document.getElementById('modalOpcionesBusqueda').style.display = 'flex';
        }

        function cerrarModalOpcionesBusqueda() {
            document.getElementById('modalOpcionesBusqueda').style.display = 'none';
        }

        // Opción 1: Búsqueda Automática
        function iniciarBusquedaAutomatica() {
            cerrarModalOpcionesBusqueda();
            realizarBusquedaAutomatica(null);
        }

        // Opción 2: URL Directo
        function solicitarURL() {
            cerrarModalOpcionesBusqueda();
            cerrarModalErrorBusqueda();
            document.getElementById('modalURL').style.display = 'flex';
            document.getElementById('inputURL').focus();
        }

        function cerrarModalURL() {
            document.getElementById('modalURL').style.display = 'none';
            document.getElementById('inputURL').value = '';
        }

        async function procesarURL() {
            const url = document.getElementById('inputURL').value.trim();
            if (!url) {
                alert("⚠️ Ingresa una URL válida");
                return;
            }
            cerrarModalURL();
            await realizarBusquedaAutomatica(url);
        }

        // Opción 3: Subir PDF/CSV
        function mostrarModalSubidaArchivo() {
            cerrarModalOpcionesBusqueda();
            cerrarModalErrorBusqueda();
            let modal = document.getElementById('modalSubidaPDF');
            if (!modal) {
                const html = `
                <div id="modalSubidaPDF" style="
                    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                    background: rgba(0,0,0,0.6); display: flex;
                    justify-content: center; align-items: center; z-index: 1500;
                ">
                    <div style="
                        background: white; padding: 30px; border-radius: 10px;
                        max-width: 450px; width: 95%; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    ">
                        <h2 style="margin-top:0; color:#1e293b; font-size:18px; font-weight:600;">Subir PDF o CSV</h2>
                        <p style="color:#475569; margin-bottom:15px;">Descarga el PDF de resultados de la carrera y súbelo aquí:</p>
                        
                        <input type="file" id="inputArchivo" accept=".pdf,.csv,.xlsx" 
                               style="width: 100%; padding: 10px; margin: 15px 0; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing:border-box; background:#FFFFFF; color:#1e293b;">
                        
                        <div style="background:#f1f5f9; padding:12px; border-radius:6px; margin:15px 0; font-size:12px; color:#475569; border-left:3px solid #007AFF;">
                            <strong style="color:#1e293b; display:block; margin-bottom:4px;">Información:</strong>
                            <div>Formatos: PDF, CSV, Excel</div>
                            <div>Tiempo: 5-10 segundos</div>
                            <div>Precisión: 99%</div>
                        </div>
                        
                        <div style="display: flex; gap: 10px; margin-top: 20px;">
                            <button onclick="cerrarModalSubida()"
                                    style="flex: 1; background: #f1f5f9; color: #1e293b; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; font-weight:500; transition:all 0.3s;" onmouseover="this.style.background='#e2e8f0'" onmouseout="this.style.background='#f1f5f9'">
                                Cancelar
                            </button>
                            <button onclick="procesarSubidaArchivo()"
                                    style="flex: 1; background: #007AFF; color: white; padding: 10px; border: none; border-radius: 6px; cursor: pointer; font-weight:500; transition:all 0.3s;" onmouseover="this.opacity='0.9'" onmouseout="this.opacity='1'">
                                Procesar
                            </button>
                        </div>
                    </div>
                </div>
                `;
                document.body.insertAdjacentHTML('beforeend', html);
                modal = document.getElementById('modalSubidaPDF');
            }
            
            modal.style.display = 'flex';
        }

        function cerrarModalSubida() {
            const modal = document.getElementById('modalSubidaPDF');
            if (modal) modal.style.display = 'none';
        }

        async function procesarSubidaArchivo() {
            const inputArchivo = document.getElementById('inputArchivo');
            const archivo = inputArchivo?.files?.[0];
            
            if (!archivo) {
                alert("⚠️ Selecciona un archivo primero");
                return;
            }
            
            const formData = new FormData();
            formData.append('file', archivo);
            formData.append('nombre_corredor', datosResultadoActual.nombreCorredor);
            formData.append('anio', datosResultadoActual.anio);
            
            const loading = document.getElementById('loading');
            const textoOriginal = loading.innerHTML;
            loading.innerHTML = '<div class=\"spinner\"></div> Procesando archivo (5-10s)...';
            loading.style.display = 'block';
            
            try {
                const response = await fetch('/resultados/buscar-archivo', {
                    method: 'POST',
                    credentials: 'include',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.encontrado) {
                    mostrarResultadoEncontrado(data);
                    cerrarModalSubida();
                    cargarCarreras();
                } else {
                    // Mostrar error con opción de reintentar otro método
                    mostrarErrorBusquedaConOpciones(`❌ No se encontró a "${datosResultadoActual.nombreCorredor}" en el archivo.\n\nVerifica el nombre en el PDF o intenta otro método.`);
                }
            } catch (err) {
                alert("❌ Error procesando archivo: " + err);
            } finally {
                loading.style.display = 'none';
                loading.innerHTML = textoOriginal;
            }
        }

        // Opción 4: Ingresar Manualmente
        function abrirModalIngresoManual() {
            cerrarModalOpcionesBusqueda();
            cerrarModalErrorBusqueda();
            
            // Limpiar campos
            document.getElementById('inputTiempo').value = '';
            document.getElementById('inputPosicion').value = '';
            document.getElementById('inputPosicionCat').value = '';
            document.getElementById('inputRitmo').value = '';
            
            document.getElementById('modalIngresoManual').style.display = 'flex';
            document.getElementById('inputTiempo').focus();
        }

        function cerrarModalIngresoManual() {
            document.getElementById('modalIngresoManual').style.display = 'none';
        }

        async function guardarClasificacionManual() {
            const tiempo = document.getElementById('inputTiempo').value.trim();
            const posicion = document.getElementById('inputPosicion').value.trim();
            const posicionCat = document.getElementById('inputPosicionCat').value.trim();
            const ritmo = document.getElementById('inputRitmo').value.trim();

            if (!tiempo || !posicion) {
                alert("⚠️ Completa al menos el tiempo y posición general");
                return;
            }

            // Validar formato de tiempo (HH:MM:SS)
            if (!/^\d{1,2}:\d{2}:\d{2}$/.test(tiempo)) {
                alert("⚠️ Formato de tiempo inválido.\nUsa: HH:MM:SS (ej: 01:45:30)");
                return;
            }

            // Validar que posición sea número
            if (isNaN(posicion)) {
                alert("⚠️ Posición debe ser un número");
                return;
            }

            // Guardar en backend
            const loading = document.getElementById('loading');
            const textoOriginal = loading.innerHTML;
            loading.innerHTML = '<div class="spinner"></div> ✅ Guardando clasificación...';
            loading.style.display = 'block';

            try {
                const response = await fetch('/resultados/buscar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        nombre_carrera: datosResultadoActual.nombreCarrera,
                        anio: datosResultadoActual.anio,
                        nombre_corredor: datosResultadoActual.nombreCorredor,
                        url_oficial: null
                    })
                });

                const data = await response.json();
                
                // Mostrar resultado
                const resultadoManual = {
                    corredor: datosResultadoActual.nombreCorredor,
                    tiempo: tiempo,
                    posicion: parseInt(posicion),
                    posicion_categoria: posicionCat ? parseInt(posicionCat) : null,
                    ritmo: ritmo || 'No especificado',
                    confianza: 1.0
                };

                mostrarResultadoEncontrado(resultadoManual);
                cerrarModalIngresoManual();
                cargarCarreras();
            } catch (err) {
                alert("❌ Error guardando resultado: " + err);
            } finally {
                loading.style.display = 'none';
                loading.innerHTML = textoOriginal;
            }
        }

        // Funciones auxiliares para búsqueda automática
        async function realizarBusquedaAutomatica(urlOficial) {
            const loading = document.getElementById('loading');
            const textoOriginal = loading.innerHTML;
            
            loading.innerHTML = '<div class="spinner"></div> 🔍 Buscando resultado (puede tardar 10-15s)...';
            loading.style.display = 'block';

            try {
                const response = await fetch('/resultados/buscar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        nombre_carrera: datosResultadoActual.nombreCarrera,
                        anio: datosResultadoActual.anio,
                        nombre_corredor: datosResultadoActual.nombreCorredor,
                        url_oficial: urlOficial || datosResultadoActual.url_oficial
                    })
                });

                const data = await response.json();
                
                if (data.encontrado) {
                    mostrarResultadoEncontrado(data);
                    cargarCarreras();
                } else {
                    // Búsqueda falló - mostrar opciones alternativas
                    mostrarErrorBusquedaConOpciones('❌ No se encontró automáticamente.');
                }
            } catch (err) {
                mostrarErrorBusquedaConOpciones('❌ Error de conexión: ' + err);
            } finally {
                loading.style.display = 'none';
                loading.innerHTML = textoOriginal;
            }
        }

        function mostrarErrorBusquedaConOpciones(mensaje) {
            // Crear modal personalizado con opciones
            let modal = document.getElementById('modalErrorBusqueda');
            if (!modal) {
                const html = `
                <div id="modalErrorBusqueda" style="
                    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                    background: rgba(0,0,0,0.6); display: flex;
                    justify-content: center; align-items: center; z-index: 1500;
                ">
                    <div style="
                        background: white; padding: 30px; border-radius: 10px;
                        max-width: 500px; width: 95%; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    ">
                        <h2 style="color:#1e293b; margin-top:0; font-size:18px; font-weight:600;" id="modalErrorMensaje"></h2>
                        <p style="color:#475569; margin:15px 0;">
                            Elige otro método de búsqueda o ingresa el resultado manualmente:
                        </p>
                        
                        <div style="display:flex; flex-direction:column; gap:10px; margin-top:20px;">
                            <button onclick="solicitarURL()" style="
                                background:white; border:2px solid #007AFF; color:#007AFF;
                                padding:12px; border-radius:6px; cursor:pointer; font-weight:500; transition:all 0.3s;
                            " onmouseover="this.style.background='#e0e7ff'" onmouseout="this.style.background='white'">
                                Pegar URL de Resultados
                            </button>
                            
                            <button onclick="mostrarModalSubidaArchivo()" style="
                                background:white; border:2px solid #007AFF; color:#007AFF;
                                padding:12px; border-radius:6px; cursor:pointer; font-weight:500; transition:all 0.3s;
                            " onmouseover="this.style.background='#e0e7ff'" onmouseout="this.style.background='white'">
                                Subir PDF o CSV
                            </button>
                            
                            <button onclick="abrirModalIngresoManual()" style="
                                background:white; border:2px solid #007AFF; color:#007AFF;
                                padding:12px; border-radius:6px; cursor:pointer; font-weight:500; transition:all 0.3s;
                            " onmouseover="this.style.background='#e0e7ff'" onmouseout="this.style.background='white'">
                                Ingresar Manualmente
                            </button>
                        </div>
                        
                        <div style="margin-top:20px; display:flex; justify-content:space-between; gap:10px;">
                            <button onclick="reabrirOpcionesBusqueda()" style="
                                background:#f1f5f9; border:1px solid #e2e8f0; color:#007AFF;
                                padding:10px 15px; border-radius:6px; cursor:pointer; flex:1; font-weight:500; transition:all 0.3s;
                            " onmouseover="this.style.background='#e2e8f0'" onmouseout="this.style.background='#f1f5f9'">
                                Atrás
                            </button>
                            <button onclick="cerrarModalErrorBusqueda()" style="
                                background:#f1f5f9; border:1px solid #e2e8f0; color:#1e293b; padding:10px 15px; 
                                border-radius:6px; cursor:pointer; flex:1; font-weight:500; transition:all 0.3s;
                            " onmouseover="this.style.background='#e2e8f0'" onmouseout="this.style.background='#f1f5f9'">
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
                `;
                document.body.insertAdjacentHTML('beforeend', html);
                modal = document.getElementById('modalErrorBusqueda');
            }
            
            document.getElementById('modalErrorMensaje').textContent = mensaje;
            modal.style.display = 'flex';
        }

        function cerrarModalErrorBusqueda() {
            const modal = document.getElementById('modalErrorBusqueda');
            if (modal) modal.style.display = 'none';
        }

        function reabrirOpcionesBusqueda() {
            cerrarModalErrorBusqueda();
            // Mostrar de nuevo el modal de opciones de búsqueda
            document.getElementById('modalOpcionesBusqueda').style.display = 'flex';
        }

        function mostrarResultadoEncontrado(data) {
            const confianza = data.confianza ? ((data.confianza || 0.7) * 100).toFixed(0) : '100';
            const posicionCategoria = data.posicion_categoria || data.posicion_categoria_descripcion || '--';
            
            const html = `
                <h2 style="color:#007AFF; margin-top:0; font-size:18px; font-weight:600;">Resultado Encontrado</h2>
                <div style="background:#f8fafc; padding:15px; border-radius:6px; margin:15px 0; border-left:3px solid #007AFF;">
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Corredor:</strong> ${data.corredor || ''}</div>
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Tiempo:</strong> <span style="color:#007AFF; font-weight:600;">${data.tiempo || data.tiempo_oficial || ''}</span></div>
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Posición General:</strong> <span style="color:#007AFF; font-weight:600;">${data.posicion || ''}</span></div>
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Posición Categoría:</strong> <span style="color:#007AFF; font-weight:600;">${posicionCategoria}</span></div>
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Ritmo:</strong> ${data.ritmo || data.ritmo_medio || '--'}</div>
                    <div style="margin:8px 0; padding-top:10px; border-top:1px solid #e2e8f0; color:#1e293b;"><strong style="color:#475569;">Confianza:</strong> <span style="color:#007AFF; font-weight:600;">${confianza}%</span></div>
                </div>
            `;
            
            document.getElementById('modalResultadoContenido').innerHTML = html;
            document.getElementById('modalResultado').style.display = 'flex';
        }

        function cerrarModalResultado() {
            document.getElementById('modalResultado').style.display = 'none';
        }

        function mostrarModalResultadoExistente(resultado) {
            const html = `
                <h2 style="color:#007AFF; margin-top:0; font-size:18px; font-weight:600;">Resultado Guardado</h2>
                <div style="background:#f8fafc; padding:15px; border-radius:6px; margin:15px 0; border-left:3px solid #007AFF;">
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Tiempo:</strong> <span style="color:#007AFF; font-weight:600;">${resultado.tiempo_oficial || 'No disponible'}</span></div>
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Posición General:</strong> <span style="color:#007AFF; font-weight:600;">${resultado.posicion_general || '--'}</span></div>
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Posición Categoría:</strong> <span style="color:#007AFF; font-weight:600;">${resultado.posicion_categoria || '--'}</span></div>
                    <div style="margin:8px 0; color:#1e293b;"><strong style="color:#475569;">Ritmo:</strong> ${resultado.ritmo_medio || '--'}</div>
                </div>
            `;
            
            document.getElementById('modalResultadoContenido').innerHTML = html;
            document.getElementById('modalResultado').style.display = 'flex';
        }

        // --- MODAL Y FUNCIONES DE SUBIDA DE ARCHIVO ---

        // --- Funciones de Compartir ---
async function compartirCalendario() {
    if (!usuarioActual) {
        document.getElementById('modalResultadoContenido').innerHTML = '<h3 style="color:#1e293b; margin-top:0; text-align:center;">Debes iniciar sesión para continuar</h3><p style="color:#475569; text-align:center; margin:15px 0;">Por favor inicia sesión en la parte superior.</p>';
        document.getElementById('modalResultado').style.display = 'flex';
        return;
    }
    try {
        const response = await fetch('/share/token', { credentials: 'include' });
        const data = await response.json();
        
        // Construct absolute URL
        const fullUrl = window.location.origin + data.share_url;
        document.getElementById('shareUrlInput').value = fullUrl;
        
        document.getElementById('modalCompartir').style.display = 'flex';
    } catch (e) {
        console.error(e);
        alert('Error al generar enlace de compartir');
    }
}

function cerrarCompartir() {
    document.getElementById('modalCompartir').style.display = 'none';
}

function copiarEnlace(event) {
    const copyText = document.getElementById("shareUrlInput");
    copyText.select();
    copyText.setSelectionRange(0, 99999); 
    navigator.clipboard.writeText(copyText.value);
    
    // Feedback visual
    const btn = event.target;
    const originalText = btn.innerText;
    btn.innerText = "¡Copiado!";
    setTimeout(() => btn.innerText = originalText, 2000);
}

// Cargar al inicio
        // cargarPerfil() se llama dentro de cargarCarreras si hay login
        cargarCarreras();
