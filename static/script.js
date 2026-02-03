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

                if (esPasada) {
                    estadoHtml = `<span class="badge cerrada" style="background-color: #7f8c8d;">Finalizada</span>`;
                    const anio = fechaCarrera.getFullYear();
                    // Pasamos el ID para buscar en cache
                    accionExtra = `<button onclick="gestionResultado(${c.id}, '${c.nombre}', ${anio})" class="btn-resultado" title="Ver mi resultado" style="margin-right:5px; background:#3498db; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">🏅</button>`;
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
                    <td>
                        ${accionExtra}
                        <button onclick="eliminarCarrera(${c.id}, '${c.nombre}')" class="btn-eliminar" title="Eliminar carrera">
                            🗑️
                        </button>
                    </td>
                </tr>`;
            });
            html += '</table>';
            listaDiv.innerHTML = html;
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

                    if (esPasada) {
                        estadoHtml = `<span class="badge cerrada" style="background-color: #7f8c8d;">🏁 Finalizada</span>`;
                        const anio = fecha.getFullYear();
                        btnResultado = `<button onclick="gestionResultado(${c.id}, '${c.nombre}', ${anio})" style="margin-top:10px; width:100%; background:#3498db; color:white; border:none; padding:8px; border-radius:4px; cursor:pointer; font-weight:bold;">🏅 Ver Resultado</button>`;
                    }

                    html += `<div class="carrera-card" style="${esPasada ? 'opacity: 0.9; background: #f4f6f7; border: 1px solid #bdc3c7;' : ''}">
                        <div class="carrera-fecha">
                            <div class="dia">${dia}</div>
                            <div class="dia-semana">${diaSemana}</div>
                        </div>
                        <div class="carrera-info">
                            <h4>${c.nombre}</h4>
                            <p><strong>📍</strong> ${c.localizacion}</p>
                            <p><strong>🏃</strong> ${c.deporte} - ${c.distancia_resumen || ''}</p>
                            ${estadoHtml}
                            ${btnResultado}
                        </div>
                        <div class="carrera-acciones">
                            <button onclick="eliminarCarrera(${c.id}, '${c.nombre}')" class="btn-eliminar" title="Eliminar carrera">
                                🗑️
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
                        <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #27ae60;">
                            <h3 style="margin-top: 0; color: #27ae60;">📋 Datos encontrados por la IA:</h3>
                            <p><strong>🏆 Nombre:</strong> ${datosEncontrados.nombre_oficial}</p>
                            <p><strong>🚴 Deporte:</strong> ${datosEncontrados.deporte}</p>
                            <p><strong>📅 Fecha:</strong> ${datosEncontrados.fecha}</p>
                            <p><strong>📍 Lugar:</strong> ${datosEncontrados.lugar}</p>
                            <p><strong>📏 Distancias:</strong> ${datosEncontrados.distancias.join(', ')}</p>
                            <p><strong>🔗 URL:</strong> ${datosEncontrados.url_oficial || 'No disponible'}</p>
                            <p><strong>📝 Estado:</strong> ${datosEncontrados.estado_inscripcion}</p>
                            
                            <div style="margin-top: 20px; display: flex; gap: 10px;">
                                <button onclick="confirmarGuardado()" style="background: #27ae60;">✅ Confirmar y Guardar</button>
                                <button onclick="cancelarBusqueda()" style="background: #e74c3c;">❌ Cancelar</button>
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

        // --- GESTIÓN DE RESULTADOS (NUEVA LÓGICA) ---
        async function gestionResultado(carreraId, nombreCarrera, anio) {
            // 1. Buscar en caché local si ya tenemos el resultado
            const carrera = carrerasCache.find(c => c.id === carreraId);
            const resultadoGuardado = carrera && carrera.resultados && carrera.resultados.length > 0 ? carrera.resultados[0] : null;

            if (resultadoGuardado) {
                 // Si ya existe, lo mostramos directo sin llamar a la API
                 alert(`
                    💾 RESULTADO GUARDADO
                    
                    ⏱️ Tiempo: ${resultadoGuardado.tiempo_oficial || 'No disponible'}
                    🏆 Pos. General: ${resultadoGuardado.posicion_general || '--'}
                    📊 Pos. Categoría: ${resultadoGuardado.posicion_general || '--'}
                    ⚡ Ritmo: ${resultadoGuardado.ritmo_medio || '--'}
                    📝 Notas: ${resultadoGuardado.comentarios || ''}
                 `);
                 return;
            }

            // 2. Si no existe, iniciamos búsqueda nueva
            let nombreCorredor = usuarioActual.nombre;
            
            if (!nombreCorredor) {
                nombreCorredor = prompt("🏁 No tienes configurado tu perfil.\nIntroduce tu nombre completo para buscar:");
                if (!nombreCorredor) return;
            } else {
                if(!confirm(`¿Buscar resultado para "${nombreCorredor}"?`)) return;
            }

            const loading = document.getElementById('loading');
            const textoOriginal = loading.innerHTML;
            
            loading.innerHTML = '<div class="spinner"></div> 🔍 Buscando tu resultado oficial...';
            loading.style.display = 'block';

            try {
                const response = await fetch('/resultados/buscar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        nombre_carrera: nombreCarrera,
                        anio: anio,
                        nombre_corredor: nombreCorredor
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.encontrado) {
                        const mensaje = `
                            🏅 ¡RESULTADO ENCONTRADO!
                            
                            🏃 Corredor: ${data.corredor}
                            ⏱️ Tiempo: ${data.tiempo}
                            🏆 Pos. General: ${data.posicion || '--'}
                            📊 Pos. Categoría: ${data.posicion_categoria || '--'}
                            ⚡ Ritmo: ${data.ritmo || '--'}
                        `;
                        alert(mensaje);
                        cargarCarreras(); 
                    } else {
                         alert("⚠️ " + data.mensaje + "\n\n(Es posible que los resultados estén en un PDF o buscador privado que no puedo leer)");
                    }
                } else {
                    const error = await response.json();
                    alert("❌ Error: " + (error.detail || "No se pudo procesar"));
                }
            } catch (err) {
                alert("❌ Error de conexión: " + err);
            } finally {
                loading.style.display = 'none';
                loading.innerHTML = textoOriginal;
            }
        }

        // --- Funciones de Compartir ---
async function compartirCalendario() {
    if (!usuarioActual) {
        alert("Debes iniciar sesión primero");
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
