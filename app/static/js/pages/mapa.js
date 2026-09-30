/* ==========================================================================
   Map Module Logic
   Extracted from: app/templates/mapa/index.html
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM Loaded, starting Map...");
    initMap();
    setupImageUpload();
    setupSearch();

    // Mobile Stability: Handle Viewport Resize
    window.addEventListener('resize', () => {
        if (map) map.invalidateSize();
    });
});

// --- GLOBAL VARIABLES ---
var map = null;
var clusterGroup = null;
var osm, satelite, topo, baseMaps, drawnItems;
var itaparicaLayer = null;

// --- Other Global Containers ---
let layers = {};
let categoriesMap = {};
let categoryLayers = {};
let categoryDummyLayers = {};
let layerControl = null;
let currentStats = {};
let statsChart = null;
let pointsLookup = {};

// Contexto Injetado via data-attribute no HTML
const containerEl = document.querySelector('.map-full-container');
const CONTEXTO_ATUAL = containerEl ? containerEl.dataset.contexto : 'geral';

// --- GIS & Modal Helpers ---
window.openModalExportar = () => {
    const modalEl = document.getElementById('modalExportar');
    if (modalEl && typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(modalEl).show();
    }
};

window.downloadExport = (formato) => {
    window.location.href = `/api/mapa/exportar?formato=${formato}&contexto=${CONTEXTO_ATUAL}`;
};

window.zoomTerritorioItaparica = () => {
    if (itaparicaLayer && map) {
        map.fitBounds(itaparicaLayer.getBounds(), { padding: [30, 30] });
    } else if (map) {
        map.flyTo([-9.400, -38.600], 9);
    }
};

window.openPointOffcanvas = (p) => {
    const titleEl = document.getElementById('offcanvasPointTitle');
    const bodyEl = document.getElementById('offcanvasPointBody');
    const offcanvasEl = document.getElementById('offcanvasPoint');

    if (!titleEl || !bodyEl || !offcanvasEl) return;

    titleEl.textContent = p.nome || 'Detalhes do Ponto';

    bodyEl.innerHTML = `
        <div class="d-grid gap-2">
            <button class="btn btn-primary btn-lg d-flex align-items-center justify-content-center gap-2 mb-2 w-100"
                onclick="window.open('https://maps.google.com/maps?q=${p.latitude},${p.longitude}', '_blank')">
                🚗 Ver no GPS
            </button>
            <button class="btn btn-outline-secondary btn-lg d-flex align-items-center justify-content-center gap-2 mb-2 w-100"
                onclick="window.closePointOffcanvas(); editarPonto(${p.id})">
                ✏️ Editar
            </button>
            <button class="btn btn-outline-danger btn-lg d-flex align-items-center justify-content-center gap-2 mb-2 w-100"
                onclick="window.closePointOffcanvas(); deletePonto(${p.id})">
                🗑️ Excluir
            </button>
        </div>
    `;

    if (typeof bootstrap !== 'undefined') {
        new bootstrap.Offcanvas(offcanvasEl).show();
    }
};

window.closePointOffcanvas = () => {
    const offcanvasEl = document.getElementById('offcanvasPoint');
    if (offcanvasEl && typeof bootstrap !== 'undefined') {
        const instance = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (instance) instance.hide();
    }
};

// --- Draw Triggers ---
window.startPolylineDraw = () => {
    if (map) new L.Draw.Polyline(map).enable();
};

// --- Action Hub & GPS Logic ---
window.openActionHub = () => {
    const offcanvasEl = document.getElementById('offcanvasActionHub');
    if (offcanvasEl && typeof bootstrap !== 'undefined') {
        new bootstrap.Offcanvas(offcanvasEl).show();
    }
};

window.getCurrentLocation = () => {
    const btn = document.querySelector('button[onclick="getCurrentLocation()"]');
    const alertContainer = document.getElementById('gpsAlertContainer');
    if (alertContainer) alertContainer.innerHTML = ''; // Clear previous

    if (!navigator.geolocation) {
        showGpsError("Geolocalização não suportada pelo navegador.");
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            document.getElementById('lat').value = lat.toFixed(6);
            document.getElementById('lng').value = lng.toFixed(6);

            // Visual Feedback
            if (btn) {
                btn.className = "btn btn-success flex-grow-1";
                btn.innerHTML = '<i class="bi bi-check-lg"></i>';
                setTimeout(() => {
                    btn.className = "btn btn-outline-primary flex-grow-1";
                    btn.innerHTML = '<i class="bi bi-crosshair"></i>';
                    btn.disabled = false;
                }, 2000);
            }

            // Map FlyTo
            if (map) map.flyTo([lat, lng], 18);
        },
        (error) => {
            console.warn("GPS Error: ", error);
            let msg = "Erro ao obter localização.";
            if (error.code === 1) msg = "Permissão de localização negada.";
            if (error.code === 2) msg = "Sinal de GPS indisponível.";
            if (error.code === 3) msg = "Tempo limite excedido.";

            showGpsError(msg);

            if (btn) {
                btn.className = "btn btn-outline-danger flex-grow-1";
                btn.innerHTML = '<i class="bi bi-exclamation-triangle"></i>';
                btn.disabled = false;
            }
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
};

function showGpsError(msg) {
    const container = document.getElementById('gpsAlertContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="alert alert-warning alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i><strong>GPS Falhou:</strong> ${msg}
            <br><small>Por favor, insira manualmente ou use a captura no mapa.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

// --- Initialize ---
async function initMap() {
    console.log("Initializing Map...");

    // 1. Base Layers
    osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' });
    satelite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { attribution: 'Tiles &copy; Esri' });
    topo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', { maxZoom: 17, attribution: 'Map data: &copy; OpenStreetMap, SRTM | Map style: &copy; OpenTopoMap' });

    baseMaps = {
        "Mapa de Rua": osm,
        "Satélite (Real)": satelite,
        "Relevo (Topográfico)": topo
    };

    // 2. Create Map Instance
    if (map) { map.remove(); }
    map = L.map('map', {
        center: [-9.400, -38.200],
        zoom: 13,
        layers: [osm],
        zoomControl: false // Reposition manually if needed, or default
    });

    // Mobile Zoom Control Positioning
    if (window.innerWidth < 768) {
        L.control.zoom({ position: 'topleft' }).addTo(map);
    } else {
        L.control.zoom({ position: 'topleft' }).addTo(map);
    }

    // 3. Setup Drawn Items
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // 4. Setup Cluster Group
    clusterGroup = L.markerClusterGroup({
        showCoverageOnHover: false,
        maxClusterRadius: 50
    });
    map.addLayer(clusterGroup);

    // 5. Setup Controls
    setupDrawControl();

    // 6. Load Data
    await loadCategories();
    await loadPontos();
    await loadTerritorioItaparica();
}

// --- Camada Vetorial Oficial: Território Itaparica (IBGE) ---
async function loadTerritorioItaparica() {
    try {
        const res = await fetch('/api/mapa/camada-itaparica');
        if (!res.ok) return;
        const geojson = await res.json();

        if (itaparicaLayer && map) {
            map.removeLayer(itaparicaLayer);
        }

        itaparicaLayer = L.geoJSON(geojson, {
            style: {
                color: '#d35400',
                weight: 2,
                dashArray: '6, 6',
                fillColor: '#f39c12',
                fillOpacity: 0.06
            },
            onEachFeature: (feature, layer) => {
                const props = feature.properties || {};
                const popupContent = `
                    <div class="p-2">
                        <div class="d-flex align-items-center mb-1">
                            <i class="bi bi-geo-alt-fill text-danger fs-5 me-2"></i>
                            <h6 class="fw-bold text-primary mb-0">${props.nome || 'Município'}</h6>
                        </div>
                        <small class="text-muted d-block mb-1">Território de Identidade Itaparica (Bahia)</small>
                        <small class="badge bg-secondary">Código IBGE: ${props.codigo_ibge || 'N/A'}</small>
                    </div>
                `;
                layer.bindPopup(popupContent);
                layer.bindTooltip(props.nome || '', { permanent: false, direction: 'center', className: 'muni-tooltip fw-bold' });
            }
        });

        itaparicaLayer.addTo(map);

        if (categoryDummyLayers) {
            categoryDummyLayers['Território Itaparica'] = itaparicaLayer;
            updateLayerList();
        }
    } catch (e) {
        console.warn("Aviso ao carregar camada do Território Itaparica:", e);
    }
}

// --- Search Logic (New) ---
function setupSearch() {
    const input = document.getElementById('searchBeneficiario');
    const resultsContainer = document.getElementById('searchResults');

    if (!input || !resultsContainer) return;

    input.addEventListener('input', function (e) {
        const term = e.target.value.toLowerCase();
        resultsContainer.innerHTML = '';

        if (term.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        // Filter and Limit to 3
        const matches = (window.allPoints || []).filter(p =>
            (p.nome && p.nome.toLowerCase().includes(term)) ||
            (p.cpf && p.cpf.includes(term))
        ).slice(0, 3);

        if (matches.length === 0) {
            resultsContainer.style.display = 'none';
            return;
        }

        matches.forEach(p => {
            const li = document.createElement('li');
            li.className = 'dropdown-item cursor-pointer border-bottom py-2';
            li.innerHTML = `
                <div class="fw-bold text-truncate">${p.nome}</div>
                <small class="text-muted">${p.tipo}</small>
             `;
            li.onclick = () => {
                // Zoom and Open
                map.flyTo([p.latitude, p.longitude], 18, { duration: 1.5 });

                // Open Popup after fly (or use 'moveend' but timeout is simpler for UX flow)
                setTimeout(() => {
                    if (pointsLookup[`${p.latitude},${p.longitude}`]) {
                        pointsLookup[`${p.latitude},${p.longitude}`].openPopup();
                    }
                }, 1600);

                // Clear Search
                input.value = '';
                resultsContainer.style.display = 'none';
            };
            resultsContainer.appendChild(li);
        });

        resultsContainer.style.display = 'block';
    });

    // Hide on click outside
    document.addEventListener('click', function (e) {
        if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.style.display = 'none';
        }
    });
}

// --- 1. Load Categories & Build UI ---
async function loadCategories() {
    try {
        const res = await fetch('/api/mapa/categorias');
        let categorias = [];
        if (res.ok) {
            categorias = await res.json();
        }

        // Tecnologias Sociais e Estruturas de Convivência com o Semiárido
        const padraoSemiárido = [
            { nome: 'Cisterna de Placa (16.000L - 1ª Água)', cor: '#0055a5' },
            { nome: 'Cisterna Calçadão (52.000L - 2ª Água)', cor: '#e67e22' },
            { nome: 'Cisterna de Enxurrada (52.000L)', cor: '#16a085' },
            { nome: 'Barreiro Trincheira', cor: '#d35400' },
            { nome: 'Barraginha', cor: '#27ae60' },
            { nome: 'Poço Tubular / Artesiano', cor: '#2980b9' },
            { nome: 'Quintal Produtivo / Agroecológico', cor: '#2ecc71' },
            { nome: 'Beneficiário', cor: '#28a745' }
        ];

        const nomesExistentes = new Set(categorias.map(c => (c.nome || '').toLowerCase()));
        padraoSemiárido.forEach(padrao => {
            if (!nomesExistentes.has(padrao.nome.toLowerCase())) {
                categorias.push(padrao);
            }
        });

        // Populate Selector Options
        const select = document.getElementById('tipo');
        if (select) {
            select.innerHTML = '';
            categorias.forEach(cat => {
                categoriesMap[cat.nome] = cat;
                const option = document.createElement('option');
                option.value = cat.nome;
                option.textContent = cat.nome;
                select.appendChild(option);
            });
        }
    } catch (e) {
        console.error(e);
        if (typeof ui !== 'undefined') ui.feedbackErro('Erro ao carregar categorias do mapa.');
    }
}

// --- Icon Logic ---
function getIconForCategory(tipo, customColor) {
    const tipoLower = (tipo || '').toLowerCase();

    // Ícone de Boneco (Beneficiário)
    if (tipoLower.includes('benefic')) {
        return L.divIcon({
            className: 'custom-pin',
            html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" style="filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.3));"> <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="${customColor || '#28a745'}" stroke="white" stroke-width="1"/> </svg>`,
            iconSize: [36, 36],
            iconAnchor: [18, 36],
            popupAnchor: [0, -38]
        });
    }

    let defaultColor = '#0055a5';
    if (tipoLower.includes('calçad') || tipoLower.includes('calcad')) defaultColor = '#e67e22';
    else if (tipoLower.includes('enxurr')) defaultColor = '#16a085';
    else if (tipoLower.includes('barreir')) defaultColor = '#d35400';
    else if (tipoLower.includes('barrag')) defaultColor = '#27ae60';
    else if (tipoLower.includes('poço') || tipoLower.includes('poco')) defaultColor = '#2980b9';
    else if (tipoLower.includes('quintal')) defaultColor = '#2ecc71';
    else if (tipoLower.includes('cistern')) defaultColor = '#0055a5';

    const color = customColor || defaultColor;

    const fullSvg = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" style="filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.3));">
            <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" fill="${color}" stroke="#ffffff" stroke-width="1.2"/>
            <path d="M12 6C12 6 15 9.5 15 11.5C15 13.16 13.66 14.5 12 14.5C10.34 14.5 9 13.16 9 11.5C9 9.5 12 6 12 6Z" fill="#ffffff"/>
        </svg>
    `;

    return L.divIcon({
        className: 'custom-pin',
        html: fullSvg,
        iconSize: [36, 36],
        iconAnchor: [18, 36],
        popupAnchor: [0, -38]
    });
}

// --- Custom Layer Control Logic ---
function setupCustomLayerControl() {
    // 1. Remove native control
    if (layerControl) {
        map.removeControl(layerControl);
        layerControl = null;
    }

    // 2. Build or Update Custom UI
    let container = document.getElementById('customLayerControl');
    if (!container) {
        // Create container if not exists (should be in HTML, but fallback here)
        container = document.createElement('div');
        container.id = 'customLayerControl';
        container.className = 'custom-layer-control glass-panel collapsed';
        container.innerHTML = `
            <button class="btn-layer-toggle" onclick="toggleLayerMenu()">
                <i class="bi bi-stack"></i>
            </button>
            <div class="layer-menu-content">
                <h6 class="fw-bold mb-2 ps-1">Camadas</h6>
                <div id="layerList" class="d-flex flex-column gap-2"></div>
            </div>
        `;
        document.body.appendChild(container); // Append to body or map wrapper

        // Ensure map wrapper has it
        const wrapper = document.querySelector('.map-full-container') || document.body;
        wrapper.appendChild(container);
    }

    updateLayerList();
}

function updateLayerList() {
    const list = document.getElementById('layerList');
    if (!list) return;
    list.innerHTML = '';

    // Base Maps
    Object.keys(baseMaps).forEach(name => {
        const layer = baseMaps[name];
        const isActive = map.hasLayer(layer);

        const item = document.createElement('div');
        item.className = `layer-item ${isActive ? 'active' : ''}`;
        item.onclick = () => {
            // Radio behavior for base maps
            Object.values(baseMaps).forEach(l => map.removeLayer(l));
            map.addLayer(layer);
            updateLayerList(); // Refresh UI
        };
        item.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="indicator-dot border border-secondary bg-light"></span>
                <span class="ms-2">${name}</span>
            </div>
            ${isActive ? '<i class="bi bi-check-circle-fill text-primary"></i>' : ''}
        `;
        list.appendChild(item);
    });

    // Separator
    const sep = document.createElement('hr');
    sep.className = 'my-1 border-secondary opacity-25';
    list.appendChild(sep);

    // Overlays (Categories)
    Object.keys(categoryDummyLayers).forEach(cat => {
        const layer = categoryDummyLayers[cat];
        const catData = categoriesMap[cat] || { cor: '#333' };
        const isActive = map.hasLayer(layer);

        const item = document.createElement('div');
        item.className = `layer-item ${isActive ? 'active' : ''}`;
        item.onclick = () => {
            if (isActive) map.removeLayer(layer);
            else map.addLayer(layer);
            updateLayerList();
        };

        item.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="indicator-dot" style="background: ${catData.cor}"></span>
                <span class="ms-2">${cat}</span>
            </div>
            ${isActive ? '<i class="bi bi-toggle-on text-success fs-5"></i>' : '<i class="bi bi-toggle-off text-muted fs-5"></i>'}
        `;
        list.appendChild(item);
    });
}

window.toggleLayerMenu = () => {
    const c = document.getElementById('customLayerControl');
    if (c) c.classList.toggle('collapsed');
}


// --- 2. Load Points (Updated with fix for undefined ID/Nome) ---
async function loadPontos() {
    try {
        const response = await fetch(`/api/mapa/pontos?contexto=${CONTEXTO_ATUAL}`);
        const pontos = await response.json();

        // Reset
        window.allPoints = pontos;

        if (clusterGroup) {
            clusterGroup.clearLayers();
        } else {
            clusterGroup = L.markerClusterGroup({
                showCoverageOnHover: false,
                maxClusterRadius: 50
            });
            map.addLayer(clusterGroup);
        }

        categoryLayers = {};
        currentStats = {};
        pointsLookup = {};
        drawnItems.clearLayers();

        pontos.forEach(p => {
            let layer;

            // Stats
            currentStats[p.tipo] = (currentStats[p.tipo] || 0) + 1;

            // Color
            const catData = categoriesMap[p.tipo] || { cor: '#6c757d' };
            const finalColor = p.cor || catData.cor;

            // Geometry
            if (p.poligono) {
                try {
                    const geoJsonGeom = JSON.parse(p.poligono);
                    layer = L.GeoJSON.geometryToLayer(geoJsonGeom);
                    if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
                        layer.setStyle({ color: finalColor, weight: 5, opacity: 0.9 });
                    } else {
                        layer.setStyle({ color: finalColor, weight: 3, fillOpacity: 0.3 });
                    }
                    drawnItems.addLayer(layer);
                } catch (e) { console.error("Bad poly", e); return; }
            } else {
                layer = L.marker([p.latitude, p.longitude], {
                    icon: getIconForCategory(p.tipo, finalColor)
                });
            }

            if (!layer) return;

            // Pass 'p' (full object) to popup
            const isMobilePopup = window.innerWidth < 768;
            if (!isMobilePopup) {
                const popupContent = createPopupContent(p, finalColor);
                layer.bindPopup(popupContent);
            }
            layer.bindTooltip(p.nome, { permanent: true, direction: 'bottom', className: 'map-label-fixed' });

            // Events
            layer.on('click', (e) => {
                const isMobileNow = window.innerWidth < 768;
                if (isMobileNow) {
                    if (e.originalEvent && typeof e.originalEvent.stopPropagation === 'function') {
                        e.originalEvent.stopPropagation();
                    }
                    map.closePopup();
                    map.flyTo([p.latitude, p.longitude], 18, { duration: 1 });
                    openPointOffcanvas(p);
                }
            });

            pointsLookup[`${p.latitude},${p.longitude}`] = layer;
            if (!categoryLayers[p.tipo]) categoryLayers[p.tipo] = [];

            if (!p.poligono) {
                categoryLayers[p.tipo].push(layer);
            }
        });

        if (!map.hasLayer(clusterGroup)) map.addLayer(clusterGroup);

        // Replace rebuildDesktopControl with Custom
        rebuildDesktopControl(); // Ensure Category Dummy Layers are built
        setupCustomLayerControl(); // Build Custom UI
        rebuildMobileFilters();

    } catch (e) {
        console.error(e);
        if (typeof ui !== 'undefined') ui.feedbackErro('Erro ao carregar pontos do mapa.');
    } finally {
        if (Object.keys(categoriesMap).length === 0) {
            console.warn("API Warning: No categories loaded or API failed.");
        }
    }
}

function createPopupContent(p, finalColor) {
    let statusBadge = '';
    const stRaw = p.status_obra || p.status_beneficiario || '';
    if (stRaw) {
        const st = stRaw.toUpperCase();
        let badgeClass = 'bg-secondary';
        if (st.includes('CONCLU') || st.includes('OK') || st.includes('USO')) badgeClass = 'bg-success';
        else if (st.includes('CONSTRU') || st.includes('OBRA')) badgeClass = 'bg-warning text-dark';
        else if (st.includes('ESCAVA')) badgeClass = 'bg-info text-dark';
        else if (st.includes('DIAGN') || st.includes('SELEC')) badgeClass = 'bg-primary';
        else if (st.includes('REFORM')) badgeClass = 'bg-danger';
        statusBadge = `<span class="badge ${badgeClass} ms-auto me-2">${stRaw}</span>`;
    }

    let bsfIcon = p.verificacao_bsf ? `<i class="bi bi-patch-check-fill text-warning fs-5" title="Verificado BSF"></i>` : '';
    const imgSrc = p.foto_url || p.foto || p.imagem || null;
    const thumbHtml = imgSrc ? `<img src="${imgSrc}" class="popup-thumb" onclick="window.open('${imgSrc}','_blank')" title="Clique para ampliar">` : '<div class="popup-thumb d-flex align-items-center justify-content-center text-muted"><small>Sem Foto</small></div>';

    const addressDest = p.full_address || `${p.latitude},${p.longitude}`;
    const responsavel = p.responsavel || "N/A";
    const safeId = p.id || '';

    let localizacao = '';
    if (p.municipio || p.comunidade) {
        localizacao = `<div class="popup-meta"><i class="bi bi-geo-alt-fill text-danger me-1"></i> <strong>${p.comunidade ? p.comunidade + ', ' : ''}${p.municipio || ''}</strong></div>`;
    }
    const benefHtml = p.beneficiario ? `<div class="popup-meta"><i class="bi bi-person-fill text-primary me-1"></i> Beneficiário: <strong>${p.beneficiario}</strong></div>` : '';
    const areaHtml = p.area_telhado ? `<div class="popup-meta"><i class="bi bi-rulers text-secondary me-1"></i> Captação: <strong>${p.area_telhado} m²</strong></div>` : '';
    const editalHtml = p.edital ? `<div class="popup-meta"><i class="bi bi-file-earmark-text text-secondary me-1"></i> Projeto: <strong>${p.edital}</strong></div>` : '';
    const dataHtml = p.data_coleta ? `<div class="popup-meta text-muted small mt-1"><i class="bi bi-calendar-event me-1"></i> Coleta: ${p.data_coleta}</div>` : '';

    return `
        <div class="popup-card-header" style="background: ${finalColor || '#666'}">
            <span>${p.tipo}</span>
            <div class="d-flex align-items-center">${statusBadge}${bsfIcon}</div>
        </div>
        <div class="popup-card-body">
            <h6 class="mb-2 fw-bold text-dark">${p.nome}</h6>
            ${thumbHtml}
            ${localizacao}
            ${benefHtml}
            ${areaHtml}
            ${editalHtml}
            <div class="popup-meta"><i class="bi bi-person-circle me-1"></i> Resp: ${responsavel}</div>
            ${p.cpf ? `<div class="popup-meta"><i class="bi bi-credit-card me-1"></i> ${p.cpf}</div>` : ''}
            ${p.descricao ? `<div class="popup-meta mt-2 fst-italic">"${p.descricao}"</div>` : ''}
            ${dataHtml}
        </div>
        <div class="popup-card-footer">
             <button onclick="editarPonto(${safeId})" class="btn btn-sm btn-outline-primary border-0 rounded-circle shadow-sm" title="Editar"><i class="bi bi-pencil-fill"></i></button>
             <a href="https://www.google.com/maps/dir/?api=1&destination=${addressDest}" target="_blank" class="btn btn-sm btn-outline-success border-0 rounded-circle shadow-sm" title="Como Chegar"><i class="bi bi-geo-alt-fill"></i></a>
             <button onclick="window.deletePonto(${safeId})" class="btn btn-sm btn-outline-danger border-0 rounded-circle shadow-sm" title="Excluir"><i class="bi bi-trash-fill"></i></button>
        </div>
     `;
}

// Logic Fix: rebuildDesktopControl still needed to populate categoryDummyLayers
function rebuildDesktopControl() {
    categoryDummyLayers = {};
    Object.keys(categoryLayers).forEach(cat => {
        const lg = L.layerGroup();
        lg.on('add', () => { if (categoryLayers[cat]) clusterGroup.addLayers(categoryLayers[cat]); });
        lg.on('remove', () => { if (categoryLayers[cat]) clusterGroup.removeLayers(categoryLayers[cat]); });
        categoryDummyLayers[cat] = lg;
        if (!map.hasLayer(lg)) map.addLayer(lg);
    });
}

window.openModalManual = () => {
    const offcanvasEl = document.getElementById('offcanvasActionHub');
    if (offcanvasEl && typeof bootstrap !== 'undefined') {
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();
    }

    const form = document.getElementById('formNovoPonto');
    if (form) form.reset();

    document.getElementById('hidden_id').value = "";
    document.getElementById('hidden_poligono').value = "";
    document.getElementById('fotoUrlHidden').value = "";
    if (document.getElementById('dataColetaHidden')) document.getElementById('dataColetaHidden').value = "";
    if (document.getElementById('municipio')) document.getElementById('municipio').value = "";
    if (document.getElementById('comunidade')) document.getElementById('comunidade').value = "";
    if (document.getElementById('beneficiario')) document.getElementById('beneficiario').value = "";
    if (document.getElementById('status_obra')) document.getElementById('status_obra').value = "Concluída / Em Uso";
    if (document.getElementById('area_telhado')) document.getElementById('area_telhado').value = "";
    if (document.getElementById('edital')) document.getElementById('edital').value = "";
    if (document.getElementById('area_calc')) document.getElementById('area_calc').value = "N/A (ponto único)";

    // Clear photo previews and alerts
    if (typeof window.removerFotoPonto === 'function') {
        window.removerFotoPonto(false);
    }

    const alertContainer = document.getElementById('gpsAlertContainer');
    if (alertContainer) alertContainer.innerHTML = '';
    const exifAlert = document.getElementById('exifGpsAlert');
    if (exifAlert) exifAlert.classList.add('d-none');
    const noExifAlert = document.getElementById('noExifGpsAlert');
    if (noExifAlert) noExifAlert.classList.add('d-none');

    // Inicializa na Etapa 1 sem forçar geolocalização automática
    setWizardStep(1);

    const modalEl = document.getElementById('modalNovoPonto');
    if (modalEl && typeof bootstrap !== 'undefined') {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }
};

// --- Wizard Step-by-Step Controller ---
window.setWizardStep = (stepNumber) => {
    // 1. Validação ao avançar além do Passo 1
    if (stepNumber > 1) {
        const lat = document.getElementById('lat')?.value;
        const lng = document.getElementById('lng')?.value;
        if (!lat || !lng) {
            if (typeof ui !== 'undefined') {
                ui.feedbackErro('Informe a localização (Foto com GPS, GPS do celular ou clique no mapa) antes de avançar.');
            }
            stepNumber = 1;
        }
    }

    // 2. Alterna visibilidade dos painéis de etapas
    for (let i = 1; i <= 4; i++) {
        const pane = document.getElementById(`wizardStep${i}`);
        const pill = document.getElementById(`wizardPill${i}`);

        if (pane) {
            if (i === stepNumber) {
                pane.classList.remove('d-none');
            } else {
                pane.classList.add('d-none');
            }
        }

        if (pill) {
            pill.classList.remove('active', 'step-completed');
            if (i === stepNumber) {
                pill.classList.add('active');
            } else if (i < stepNumber) {
                pill.classList.add('step-completed');
            }
        }
    }

    // 3. Atualiza indicador textual no cabeçalho
    const stepLabels = [
        "Passo 1 de 4: Foto & Localização",
        "Passo 2 de 4: Tecnologia Social",
        "Passo 3 de 4: Beneficiário & Território",
        "Passo 4 de 4: Projeto & Revisão"
    ];
    const indicator = document.getElementById('wizardStepIndicator');
    if (indicator && stepLabels[stepNumber - 1]) {
        indicator.textContent = stepLabels[stepNumber - 1];
    }

    // 4. Se for o passo 4, atualiza o card de resumo
    if (stepNumber === 4) {
        updateWizardSummary();
    }
};

window.autoSugerirNomePonto = (force = false) => {
    const nomeInput = document.getElementById('nome');
    if (!nomeInput) return;
    if (!force && nomeInput.value.trim() !== '') return;

    const tipoSelect = document.getElementById('tipo');
    const benefInput = document.getElementById('beneficiario');
    const comInput = document.getElementById('comunidade');

    const tipoRaw = tipoSelect ? tipoSelect.value : 'Ponto';
    const tipoCurto = tipoRaw.split('(')[0].trim();
    const benef = benefInput ? benefInput.value.trim() : '';
    const com = comInput ? comInput.value.trim() : '';

    let sugestao = tipoCurto;
    if (benef) {
        sugestao += ` - ${benef}`;
    } else if (com) {
        sugestao += ` - ${com}`;
    }

    nomeInput.value = sugestao;
};

function updateWizardSummary() {
    const nome = document.getElementById('nome')?.value || 'Não informado';
    const tipo = document.getElementById('tipo')?.value || 'Não informado';
    const status = document.getElementById('status_obra')?.value || 'Concluída / Em Uso';
    const benef = document.getElementById('beneficiario')?.value || 'Não informado';
    const muni = document.getElementById('municipio')?.value || '';
    const com = document.getElementById('comunidade')?.value || '';
    const lat = document.getElementById('lat')?.value || '';
    const lng = document.getElementById('lng')?.value || '';
    const fotoUrl = document.getElementById('fotoUrlHidden')?.value || '';

    const sumNome = document.getElementById('sumNome');
    if (sumNome) sumNome.textContent = nome;

    const sumTipo = document.getElementById('sumTipo');
    if (sumTipo) sumTipo.textContent = tipo;

    const sumStatus = document.getElementById('sumStatus');
    if (sumStatus) sumStatus.textContent = status;

    const sumBenef = document.getElementById('sumBeneficiario');
    if (sumBenef) sumBenef.textContent = benef;

    const sumLocal = document.getElementById('sumLocal');
    if (sumLocal) {
        const localParts = [com, muni].filter(Boolean);
        sumLocal.textContent = localParts.length > 0 ? localParts.join(', ') : 'Território Itaparica';
    }

    const sumCoords = document.getElementById('sumCoords');
    if (sumCoords) {
        sumCoords.textContent = (lat && lng) ? `${lat}, ${lng}` : 'Nenhuma coordenada';
    }

    const sumFotoPreview = document.getElementById('sumFotoPreview');
    const sumSemFoto = document.getElementById('sumSemFoto');
    if (sumFotoPreview && sumSemFoto) {
        if (fotoUrl) {
            sumFotoPreview.src = fotoUrl;
            sumFotoPreview.classList.remove('d-none');
            sumSemFoto.classList.add('d-none');
        } else {
            sumFotoPreview.src = '';
            sumFotoPreview.classList.add('d-none');
            sumSemFoto.classList.remove('d-none');
        }
    }
}


function rebuildMobileFilters() {
    const body = document.getElementById('mobileFilterBody');
    if (!body) return;
    body.innerHTML = '';
    // body.style.padding = '0'; // Layout handled by Offcanvas

    const listGroup = document.createElement('ul');
    listGroup.className = 'list-group list-group-flush';

    Object.keys(categoryLayers).forEach(cat => {
        const catData = categoriesMap[cat] ? categoriesMap[cat] : { cor: '#333' };

        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center py-3 border-light';

        const isChecked = map.hasLayer(categoryDummyLayers[cat]);

        listItem.innerHTML = `
            <div class="d-flex align-items-center">
                <span style='display:inline-block;width:16px;height:16px;background:${catData.cor};border-radius:50%;margin-right:12px;border:2px solid #fff;box-shadow:0 0 2px rgba(0,0,0,0.2);'></span>
                <span class="fw-medium text-dark">${cat}</span>
                <span class="badge bg-light text-secondary ms-2 rounded-pill">${categoryLayers[cat].length}</span>
            </div>
            <div class="form-check form-switch m-0">
                <input class="form-check-input large-switch" type="checkbox" id="filter-${cat}" ${isChecked ? 'checked' : ''} onchange="toggleCategory('${cat}', this.checked)">
            </div>
        `;
        listGroup.appendChild(listItem);
    });

    body.appendChild(listGroup);
}

window.toggleCategory = (cat, isChecked) => {
    const lg = categoryDummyLayers[cat];
    if (!lg) return;

    if (isChecked) {
        if (!map.hasLayer(lg)) map.addLayer(lg);
    } else {
        if (map.hasLayer(lg)) map.removeLayer(lg);
    }
};

// Rename to openFilterOffcanvas
window.openFilterOffcanvas = () => {
    Object.keys(categoryDummyLayers).forEach(cat => {
        const lg = categoryDummyLayers[cat];
        const checkbox = document.getElementById(`filter-${cat}`);
        if (lg && checkbox) {
            checkbox.checked = map.hasLayer(lg);
        }
    });

    const offcanvasEl = document.getElementById('offcanvasFilters');
    if (offcanvasEl && typeof bootstrap !== 'undefined') {
        const offcanvas = bootstrap.Offcanvas.getOrCreateInstance(offcanvasEl);
        offcanvas.show();
    }
};
// Legacy/Alias
window.openFilterModal = window.openFilterOffcanvas;

window.confirmFilters = () => {
    const offcanvasEl = document.getElementById('offcanvasFilters');
    if (offcanvasEl && typeof bootstrap !== 'undefined') {
        const offcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (offcanvas) offcanvas.hide();
    }
    if (typeof ui !== 'undefined') ui.feedbackSucesso('Filtros atualizados com sucesso!');
};

function setupDrawControl() {
    if (typeof L.Control.Draw === 'undefined') return;

    var drawControl = new L.Control.Draw({
        draw: {
            polyline: true, marker: true, circle: false, circlemarker: false,
            polygon: { allowIntersection: false, showArea: true },
            rectangle: true
        },
        edit: { featureGroup: drawnItems }
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (e) {
        var type = e.layerType;
        var layer = e.layer;
        drawnItems.addLayer(layer);

        let geoJson = layer.toGeoJSON();
        let geometry = JSON.stringify(geoJson.geometry);
        let areaCalc = "N/A";

        if (type === 'polygon' || type === 'rectangle') {
            // Check if turf is loaded
            if (typeof turf !== 'undefined') {
                const area = turf.area(geoJson);
                areaCalc = (area > 10000) ? (area / 10000).toFixed(2) + " ha" : area.toFixed(2) + " m²";
            }
        }

        document.getElementById('formNovoPonto').reset();
        document.getElementById('hidden_id').value = "";
        document.getElementById('hidden_poligono').value = geometry;
        const areaInput = document.getElementById('area_calc');
        if (areaInput) areaInput.value = areaCalc;

        if (type === 'marker') {
            document.getElementById('lat').value = layer.getLatLng().lat;
            document.getElementById('lng').value = layer.getLatLng().lng;
            document.getElementById('hidden_poligono').value = "";
        } else {
            const center = layer.getBounds().getCenter();
            document.getElementById('lat').value = center.lat;
            document.getElementById('lng').value = center.lng;
        }

        setWizardStep(1);
        const modalEl = document.getElementById('modalNovoPonto');
        if (modalEl && typeof bootstrap !== 'undefined') {
            bootstrap.Modal.getOrCreateInstance(modalEl).show();
        }
    });
}

function setupImageUpload() {
    const fotoInput = document.getElementById('fotoInput');
    const fotoHidden = document.getElementById('fotoUrlHidden');
    const uploadStatus = document.getElementById('uploadStatus');
    const previewContainer = document.getElementById('fotoPreviewContainer');
    const previewImg = document.getElementById('fotoPreviewImg');
    const exifAlert = document.getElementById('exifGpsAlert');
    const noExifAlert = document.getElementById('noExifGpsAlert');
    const dataBadge = document.getElementById('dataColetaBadge');
    const dataHidden = document.getElementById('dataColetaHidden');

    if (!fotoInput) return;

    fotoInput.addEventListener('change', async function () {
        if (!this.files || !this.files[0]) return;

        const file = this.files[0];
        const formData = new FormData();
        formData.append('file', file);

        if (uploadStatus) {
            uploadStatus.classList.remove('d-none');
            uploadStatus.innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div>';
        }
        if (exifAlert) exifAlert.classList.add('d-none');
        if (noExifAlert) noExifAlert.classList.add('d-none');

        try {
            const res = await fetch('/api/mapa/upload', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Erro no upload");

            const data = await res.json();
            if (fotoHidden) fotoHidden.value = data.url;

            if (uploadStatus) {
                uploadStatus.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
                uploadStatus.classList.remove('d-none');
            }

            // Preview Thumbnail
            if (previewContainer && previewImg) {
                previewImg.src = data.url;
                previewContainer.classList.remove('d-none');
            }

            // EXIF GPS Detection (Timestamp Camera / Smartphone)
            if (data.has_gps && data.latitude && data.longitude) {
                const latInput = document.getElementById('lat');
                const lngInput = document.getElementById('lng');
                if (latInput) {
                    latInput.value = Number(data.latitude).toFixed(6);
                    latInput.classList.add('border-success', 'bg-success-subtle');
                    setTimeout(() => latInput.classList.remove('border-success', 'bg-success-subtle'), 3500);
                }
                if (lngInput) {
                    lngInput.value = Number(data.longitude).toFixed(6);
                    lngInput.classList.add('border-success', 'bg-success-subtle');
                    setTimeout(() => lngInput.classList.remove('border-success', 'bg-success-subtle'), 3500);
                }

                if (data.data_coleta) {
                    if (dataHidden) dataHidden.value = data.data_coleta;
                    if (dataBadge) {
                        dataBadge.textContent = 'Data da Foto: ' + data.data_coleta;
                        dataBadge.classList.remove('d-none');
                    }
                }

                if (exifAlert) exifAlert.classList.remove('d-none');
                if (noExifAlert) noExifAlert.classList.add('d-none');

                const alertContainer = document.getElementById('gpsAlertContainer');
                if (alertContainer) alertContainer.innerHTML = '';

                if (typeof ui !== 'undefined') {
                    ui.feedbackSucesso('Localização e data extraídas da foto com sucesso!');
                }

                if (map) {
                    map.flyTo([data.latitude, data.longitude], 17, { duration: 1.5 });
                }
            } else {
                if (noExifAlert) noExifAlert.classList.remove('d-none');
                if (exifAlert) exifAlert.classList.add('d-none');
            }

        } catch (e) {
            console.error("Upload error:", e);
            if (typeof ui !== 'undefined') ui.feedbackErro('Falha ao fazer upload da imagem.');
            if (uploadStatus) uploadStatus.classList.add('d-none');
            this.value = '';
        }
    });
}

window.removerFotoPonto = (clearFile = true) => {
    const fotoInput = document.getElementById('fotoInput');
    const fotoHidden = document.getElementById('fotoUrlHidden');
    const previewContainer = document.getElementById('fotoPreviewContainer');
    const previewImg = document.getElementById('fotoPreviewImg');
    const exifAlert = document.getElementById('exifGpsAlert');
    const noExifAlert = document.getElementById('noExifGpsAlert');
    const dataBadge = document.getElementById('dataColetaBadge');
    const dataHidden = document.getElementById('dataColetaHidden');
    const uploadStatus = document.getElementById('uploadStatus');

    if (clearFile && fotoInput) fotoInput.value = '';
    if (fotoHidden) fotoHidden.value = '';
    if (dataHidden) dataHidden.value = '';
    if (previewContainer) previewContainer.classList.add('d-none');
    if (previewImg) previewImg.src = '';
    if (exifAlert) exifAlert.classList.add('d-none');
    if (noExifAlert) noExifAlert.classList.add('d-none');
    if (dataBadge) dataBadge.classList.add('d-none');
    if (uploadStatus) uploadStatus.classList.add('d-none');
};

// --- CRUD Actions ---
window.salvarPonto = async (event) => {
    event.preventDefault();

    const id = document.getElementById('hidden_id').value;
    const lat = document.getElementById('lat').value;
    const lng = document.getElementById('lng').value;
    const nome = document.getElementById('nome').value;
    const tipo = document.getElementById('tipo').value;
    const municipio = document.getElementById('municipio') ? document.getElementById('municipio').value : null;
    const comunidade = document.getElementById('comunidade') ? document.getElementById('comunidade').value : null;
    const beneficiario = document.getElementById('beneficiario') ? document.getElementById('beneficiario').value : null;
    const status_obra = document.getElementById('status_obra') ? document.getElementById('status_obra').value : null;
    const area_telhado = document.getElementById('area_telhado') && document.getElementById('area_telhado').value ? parseFloat(document.getElementById('area_telhado').value) : null;
    const edital = document.getElementById('edital') ? document.getElementById('edital').value : null;
    const data_coleta = document.getElementById('dataColetaHidden') ? document.getElementById('dataColetaHidden').value : null;
    const foto_url = document.getElementById('fotoUrlHidden') ? document.getElementById('fotoUrlHidden').value : null;
    const descricao = document.getElementById('descricao').value;
    const poligono = document.getElementById('hidden_poligono').value;
    const cor = document.getElementById('cor').value;

    // Validações Essenciais
    if (!lat || !lng || isNaN(parseFloat(lat)) || isNaN(parseFloat(lng))) {
        if (typeof ui !== 'undefined') {
            ui.feedbackErro('As coordenadas (Latitude e Longitude) são obrigatórias.');
        }
        setWizardStep(1);
        return;
    }

    if (!nome || nome.trim() === '') {
        if (typeof ui !== 'undefined') {
            ui.feedbackErro('Por favor, informe a identificação / nome do ponto.');
        }
        setWizardStep(3);
        return;
    }

    const btnSalvar = document.getElementById('btnSalvar');
    const oldBtnHtml = btnSalvar ? btnSalvar.innerHTML : '';
    if (btnSalvar) {
        btnSalvar.disabled = true;
        btnSalvar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Salvando...';
    }

    const payload = {
        latitude: parseFloat(lat),
        longitude: parseFloat(lng),
        nome: nome,
        tipo: tipo,
        municipio: municipio,
        comunidade: comunidade,
        beneficiario: beneficiario,
        status_obra: status_obra,
        area_telhado: area_telhado,
        edital: edital,
        data_coleta: data_coleta,
        foto_url: foto_url,
        imagem: foto_url,
        descricao: descricao,
        poligono: poligono || null,
        cor: cor,
        contexto: CONTEXTO_ATUAL
    };

    const url = id ? `/api/mapa/pontos/${id}` : '/api/mapa/pontos';
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Erro ao salvar");

        await initMap();
        const modalEl = document.getElementById('modalNovoPonto');
        if (modalEl && typeof bootstrap !== 'undefined') {
            const inst = bootstrap.Modal.getInstance(modalEl);
            if (inst) inst.hide();
        }
        if (typeof ui !== 'undefined') ui.feedbackSucesso('Ponto salvo com sucesso!');

    } catch (e) {
        console.error(e);
        if (typeof ui !== 'undefined') ui.feedbackErro('Erro ao salvar ponto. Verifique os dados.');
    } finally {
        if (btnSalvar) {
            btnSalvar.disabled = false;
            btnSalvar.innerHTML = oldBtnHtml;
        }
    }
};

window.deletePonto = async (id) => {
    if (typeof ui === 'undefined') return;

    ui.confirmarExclusao(async () => {
        try {
            const res = await fetch(`/api/mapa/pontos/${id}`, { method: 'DELETE' });
            if (res.ok) {
                ui.feedbackSucesso('Ponto excluído com sucesso!');
                initMap();
            } else {
                ui.feedbackErro('Erro ao excluir o ponto.');
            }
        } catch (e) {
            ui.feedbackErro('Erro de conexão.');
        }
    });
};

window.editarPonto = async (id) => {
    try {
        const res = await fetch(`/api/mapa/pontos/${id}`);
        if (!res.ok) throw new Error();
        const ponto = await res.json();

        document.getElementById('hidden_id').value = ponto.id;
        document.getElementById('nome').value = ponto.nome || '';
        document.getElementById('tipo').value = ponto.tipo || '';
        if (document.getElementById('municipio')) document.getElementById('municipio').value = ponto.municipio || '';
        if (document.getElementById('comunidade')) document.getElementById('comunidade').value = ponto.comunidade || '';
        if (document.getElementById('beneficiario')) document.getElementById('beneficiario').value = ponto.beneficiario || '';
        if (document.getElementById('status_obra')) document.getElementById('status_obra').value = ponto.status_obra || ponto.status_beneficiario || 'Concluída / Em Uso';
        if (document.getElementById('area_telhado')) document.getElementById('area_telhado').value = ponto.area_telhado || '';
        if (document.getElementById('edital')) document.getElementById('edital').value = ponto.edital || '';
        if (document.getElementById('descricao')) document.getElementById('descricao').value = ponto.descricao || '';
        document.getElementById('lat').value = ponto.latitude;
        document.getElementById('lng').value = ponto.longitude;
        document.getElementById('cor').value = ponto.cor || categoriesMap[ponto.tipo]?.cor || '#3388ff';
        document.getElementById('hidden_poligono').value = ponto.poligono || '';

        // Foto preview
        const fotoUrl = ponto.foto_url || ponto.foto || ponto.imagem || '';
        document.getElementById('fotoUrlHidden').value = fotoUrl;
        const previewContainer = document.getElementById('fotoPreviewContainer');
        const previewImg = document.getElementById('fotoPreviewImg');
        if (fotoUrl && previewContainer && previewImg) {
            previewImg.src = fotoUrl;
            previewContainer.classList.remove('d-none');
        } else if (previewContainer) {
            previewContainer.classList.add('d-none');
        }

        // Data de coleta
        if (ponto.data_coleta) {
            if (document.getElementById('dataColetaHidden')) document.getElementById('dataColetaHidden').value = ponto.data_coleta;
            const dataBadge = document.getElementById('dataColetaBadge');
            if (dataBadge) {
                dataBadge.textContent = 'Data: ' + ponto.data_coleta;
                dataBadge.classList.remove('d-none');
            }
        }

        // Area Calc Display
        if (ponto.poligono && typeof turf !== 'undefined') {
            try {
                const area = turf.area(JSON.parse(ponto.poligono));
                document.getElementById('area_calc').value = (area > 10000) ? (area / 10000).toFixed(2) + " ha" : area.toFixed(2) + " m²";
            } catch (e) { document.getElementById('area_calc').value = "N/A"; }
        } else {
            const areaInput = document.getElementById('area_calc');
            if (areaInput) areaInput.value = "N/A (ponto único)";
        }

        // Initialize wizard at Step 1
        setWizardStep(1);

        const modalEl = document.getElementById('modalNovoPonto');
        if (modalEl && typeof bootstrap !== 'undefined') {
            bootstrap.Modal.getOrCreateInstance(modalEl).show();
        }
    } catch (e) {
        console.error(e);
        if (typeof ui !== 'undefined') ui.feedbackErro('Erro ao carregar dados do ponto.');
    }
};

function openBottomSheet(p) {
    const sheet = document.getElementById('mobileBottomSheet');
    const body = document.getElementById('bottomSheetBody');
    if (!sheet || !body) return;

    const imgSrc = p.foto_url || p.foto || p.imagem || null;
    const thumbHtml = imgSrc
        ? `<img src="${imgSrc}" class="w-100 rounded mb-3 shadow-sm" style="max-height: 220px; object-fit: cover;" onclick="window.open('${imgSrc}','_blank')">`
        : '';

    let statusBadge = '';
    const stRaw = p.status_obra || p.status_beneficiario || '';
    if (stRaw) {
        statusBadge = `<span class="badge bg-primary mb-2">${stRaw}</span>`;
    }

    let localizacao = '';
    if (p.municipio || p.comunidade) {
        localizacao = `<p class="mb-1 text-danger fw-semibold"><i class="bi bi-geo-alt-fill me-1"></i>${p.comunidade ? p.comunidade + ', ' : ''}${p.municipio || ''}</p>`;
    }
    const benefHtml = p.beneficiario ? `<p class="mb-1 text-muted"><i class="bi bi-person-fill me-1"></i>Beneficiário: <strong>${p.beneficiario}</strong></p>` : '';
    const areaHtml = p.area_telhado ? `<p class="mb-1 text-muted"><i class="bi bi-rulers me-1"></i>Captação: <strong>${p.area_telhado} m²</strong></p>` : '';

    body.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
             <h5 class="fw-bold mb-0">${p.nome}</h5>
             ${statusBadge}
        </div>
        ${localizacao}
        ${thumbHtml}
        ${benefHtml}
        ${areaHtml}
        <p class="text-muted"><i class="bi bi-tag-fill me-2"></i>${p.tipo}</p>
        <p class="mb-4 text-secondary">${p.descricao || 'Sem descrição.'}</p>
        
        <div class="d-grid gap-2">
            <a href="https://www.google.com/maps/dir/?api=1&destination=${p.latitude},${p.longitude}" target="_blank" class="btn btn-success">
                <i class="bi bi-geo-alt-fill me-2"></i>Como Chegar
            </a>
            <div class="row g-2">
                <div class="col-6">
                    <button onclick="editarPonto(${p.id}); closeBottomSheet()" class="btn btn-outline-primary w-100">
                        <i class="bi bi-pencil me-1"></i>Editar
                    </button>
                </div>
                <div class="col-6">
                    <button onclick="window.deletePonto(${p.id}); closeBottomSheet()" class="btn btn-outline-danger w-100">
                        <i class="bi bi-trash me-1"></i>Excluir
                    </button>
                </div>
            </div>
        </div>
    `;

    sheet.classList.add('show');
}

window.closeBottomSheet = () => {
    const sheet = document.getElementById('mobileBottomSheet');
    if (sheet) sheet.classList.remove('show');
}

// Misc Tools
window.toggleFullScreen = () => {
    if (!document.fullscreenElement) {
        document.getElementById('mapa-wrapper').requestFullscreen().catch(err => {
            console.warn(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
        });
    } else {
        document.exitFullscreen();
    }
}



// --- Modal Helpers (Close Offcanvas first) ---
window.openModalImport = () => {
    // Context Cleanup
    const offcanvasEl = document.getElementById('offcanvasActionHub');
    if (offcanvasEl) {
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();
    }
    const modalEl = document.getElementById('modalImport');
    if (modalEl) new bootstrap.Modal(modalEl).show();
}

window.openModalStats = () => {
    // Stats usually from Toolbar, but safe to close offcanvas if open
    const offcanvasEl = document.getElementById('offcanvasActionHub');
    if (offcanvasEl) {
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();
    }

    updateStatsChart();

    const modalEl = document.getElementById('modalStats');
    if (modalEl) new bootstrap.Modal(modalEl).show();
}

function updateStatsChart() {
    const ctx = document.getElementById('statsChart');
    const tableBody = document.getElementById('statsTableBody');
    if (!ctx || !tableBody) return;

    // Table
    tableBody.innerHTML = '';
    const sorted = Object.entries(currentStats).sort((a, b) => b[1] - a[1]);

    // Chart Data
    const labels = [];
    const data = [];
    const colors = [];

    sorted.forEach(([type, count]) => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${type}</td><td class="text-end fw-bold">${count}</td>`;
        tableBody.appendChild(row);

        labels.push(type);
        data.push(count);
        colors.push(categoriesMap[type]?.cor || '#666');
    });

    // Destroy old chart
    if (statsChart) statsChart.destroy();

    // Create Chart
    statsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12 } }
            }
        }
    });

}

window.captureOnMap = () => {
    if (!map) return;

    // Close modal momentarily
    const modalEl = document.getElementById('modalNovoPonto');
    let modal = null;
    if (modalEl && typeof bootstrap !== 'undefined') {
        modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3500,
            icon: 'info',
            title: 'Toque no mapa para marcar a localização'
        });
    }

    const container = document.getElementById('map');
    if (container) container.classList.add('cursor-crosshair');

    map.once('click', function (e) {
        const latInput = document.getElementById('lat');
        const lngInput = document.getElementById('lng');
        if (latInput) latInput.value = e.latlng.lat.toFixed(6);
        if (lngInput) lngInput.value = e.latlng.lng.toFixed(6);
        if (container) container.classList.remove('cursor-crosshair');

        if (modalEl && typeof bootstrap !== 'undefined') {
            const m = bootstrap.Modal.getOrCreateInstance(modalEl);
            m.show();
            setWizardStep(1);
        }
        if (typeof ui !== 'undefined') {
            ui.feedbackSucesso('Localização capturada do mapa!');
        }
    });
};
