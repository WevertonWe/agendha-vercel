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
        if (!res.ok) throw new Error("Erro ao carregar categorias");
        const categorias = await res.json();

        // Populate Selector Options Only
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
    const tipoLower = tipo.toLowerCase();

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

    const colors = {
        'Cisterna': '#003366',
        'Barreiro': '#D2691E',
        'Calçadão': '#808080',
        'Área de Roça': '#90EE90',
        'Default': '#3388ff'
    };

    const icons = {
        'Cisterna': '<path d="M12 2L12 22M2 12L22 12" stroke="white" stroke-width="2"/> <path d="M12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22Z" fill="{color}" /> <path d="M12 6C12 6 16 10 16 14C16 16.2 14.2 18 12 18C9.8 18 8 16.2 8 14C8 10 12 6 12 6Z" fill="white"/>',
        'Barreiro': '<rect x="4" y="8" width="16" height="10" rx="2" fill="{color}" /> <path d="M6 8L6 6C6 4.9 6.9 4 8 4H16C17.1 4 18 4.9 18 6L18 8" stroke="{color}" stroke-width="2" fill="none"/>',
        'Default': '<path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" fill="{color}" /> <circle cx="12" cy="9" r="2.5" fill="white"/>'
    };

    const color = customColor || colors[tipo] || colors['Default'];
    let svgContent = icons[tipo] || icons['Default'];
    svgContent = svgContent.replaceAll('{color}', color);

    const fullSvg = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" style="filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.3));">
            ${svgContent}
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
    if (p.status_beneficiario) {
        const st = p.status_beneficiario.toUpperCase();
        let badgeClass = 'bg-secondary';
        if (st.includes('IMPORTADO')) badgeClass = 'bg-primary';
        if (st.includes('CADASTRADO') || st.includes('OK')) badgeClass = 'bg-success';
        if (st.includes('CONSTRU')) badgeClass = 'bg-warning text-dark';
        statusBadge = `<span class="badge ${badgeClass} ms-auto me-2">${p.status_beneficiario}</span>`;
    }
    let bsfIcon = p.verificacao_bsf ? `<i class="bi bi-patch-check-fill text-warning fs-5" title="Verificado BSF"></i>` : '';
    const imgSrc = p.foto || p.imagem || null;
    const thumbHtml = imgSrc ? `<img src="${imgSrc}" class="popup-thumb" onclick="window.open('${imgSrc}','_blank')">` : '<div class="popup-thumb d-flex align-items-center justify-content-center text-muted"><small>Sem Imagem</small></div>';

    const addressDest = p.full_address || `${p.latitude},${p.longitude}`;
    const responsavel = p.responsavel || "N/A";

    // Escape ID for safety if string, but it's usually int.
    // Ensure p.id is present.
    const safeId = p.id || '';

    return `
        <div class="popup-card-header" style="background: ${finalColor || '#666'}">
            <span>${p.tipo}</span>
            <div class="d-flex align-items-center">${statusBadge}${bsfIcon}</div>
        </div>
        <div class="popup-card-body">
            <h6 class="mb-2 fw-bold text-dark">${p.nome}</h6>
            ${thumbHtml}
            <div class="popup-meta"><i class="bi bi-person-circle me-1"></i> ${responsavel}</div>
            ${p.cpf ? `<div class="popup-meta"><i class="bi bi-credit-card me-1"></i> ${p.cpf}</div>` : ''}
            ${p.descricao ? `<div class="popup-meta mt-2 fst-italic">"${p.descricao}"</div>` : ''}
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
    // Don't add Native Control
}

window.openModalManual = () => {
    // Context Cleanup: Close Action Hub
    const offcanvasEl = document.getElementById('offcanvasActionHub');
    if (offcanvasEl) {
        // Force hide by removing show class/backdrop if instance check is hard, 
        // or use bootstrap API if available.
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();
    }

    document.getElementById('formNovoPonto').reset();
    document.getElementById('hidden_id').value = "";
    document.getElementById('hidden_poligono').value = "";

    // Clear Alerts
    const alertContainer = document.getElementById('gpsAlertContainer');
    if (alertContainer) alertContainer.innerHTML = '';

    // Auto-trigger GPS
    getCurrentLocation();

    // Use specific ID
    const modalEl = document.getElementById('modalNovoPonto');
    if (modalEl && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
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

        const modalEl = document.getElementById('modalNovoPonto');
        if (modalEl) new bootstrap.Modal(modalEl).show();
    });
}

function setupImageUpload() {
    const fotoInput = document.getElementById('fotoInput');
    const fotoHidden = document.getElementById('fotoUrlHidden');
    const uploadStatus = document.getElementById('uploadStatus');

    if (!fotoInput) return;

    fotoInput.addEventListener('change', async function () {
        if (!this.files || !this.files[0]) return;

        const file = this.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            uploadStatus.classList.remove('d-none');
            uploadStatus.innerHTML = '<div class="spinner-border spinner-border-sm text-secondary"></div>';

            const res = await fetch('/api/mapa/upload', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Erro no upload");

            const data = await res.json();
            fotoHidden.value = data.url;
            uploadStatus.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
            uploadStatus.classList.remove('d-none');

        } catch (e) {
            console.error(e);
            if (typeof ui !== 'undefined') ui.feedbackErro('Falha ao fazer upload da imagem.');
            uploadStatus.classList.add('d-none');
            this.value = '';
        }
    });
}

// --- CRUD Actions ---
window.salvarPonto = async (event) => {
    event.preventDefault();

    const id = document.getElementById('hidden_id').value;
    const lat = document.getElementById('lat').value;
    const lng = document.getElementById('lng').value;
    const nome = document.getElementById('nome').value;
    const tipo = document.getElementById('tipo').value;
    const descricao = document.getElementById('descricao').value;
    const poligono = document.getElementById('hidden_poligono').value;
    const cor = document.getElementById('cor').value;
    const imagem = document.getElementById('fotoUrlHidden').value;

    const payload = {
        latitude: parseFloat(lat),
        longitude: parseFloat(lng),
        nome: nome,
        tipo: tipo,
        descricao: descricao,
        poligono: poligono || null,
        cor: cor,
        contexto: CONTEXTO_ATUAL,
        imagem: imagem
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
        bootstrap.Modal.getInstance(modalEl).hide();
        if (typeof ui !== 'undefined') ui.feedbackSucesso('Ponto salvo com sucesso!');

    } catch (e) {
        console.error(e);
        if (typeof ui !== 'undefined') ui.feedbackErro('Erro ao salvar ponto. Verifique os dados.');
    }
}

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
        document.getElementById('nome').value = ponto.nome;
        document.getElementById('tipo').value = ponto.tipo;
        document.getElementById('descricao').value = ponto.descricao || '';
        document.getElementById('lat').value = ponto.latitude;
        document.getElementById('lng').value = ponto.longitude;
        document.getElementById('cor').value = ponto.cor || categoriesMap[ponto.tipo]?.cor || '#3388ff';
        document.getElementById('hidden_poligono').value = ponto.poligono || '';

        // Area Calc Display
        if (ponto.poligono && typeof turf !== 'undefined') {
            try {
                const area = turf.area(JSON.parse(ponto.poligono));
                document.getElementById('area_calc').value = (area > 10000) ? (area / 10000).toFixed(2) + " ha" : area.toFixed(2) + " m²";
            } catch (e) { document.getElementById('area_calc').value = "N/A"; }
        } else { document.getElementById('area_calc').value = ""; }

        const modalEl = document.getElementById('modalNovoPonto');
        if (modalEl) new bootstrap.Modal(modalEl).show();
    } catch (e) {
        if (typeof ui !== 'undefined') ui.feedbackErro('Erro ao carregar dados do ponto.');
    }
};

function openBottomSheet(p) {
    const sheet = document.getElementById('mobileBottomSheet');
    const body = document.getElementById('bottomSheetBody');
    if (!sheet || !body) return;

    const imgSrc = p.foto || p.imagem || null;
    const thumbHtml = imgSrc
        ? `<img src="${imgSrc}" class="w-100 rounded mb-3" style="height: 200px; object-fit: cover;" onclick="window.open('${imgSrc}','_blank')">`
        : '';

    let statusBadge = '';
    if (p.status_beneficiario) {
        statusBadge = `<span class="badge bg-secondary mb-2">${p.status_beneficiario}</span>`;
    }

    body.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
             <h5 class="fw-bold mb-0">${p.nome}</h5>
             ${statusBadge}
        </div>
        ${thumbHtml}
        <p class="text-muted"><i class="bi bi-tag-fill me-2"></i>${p.tipo}</p>
        <p class="mb-4">${p.descricao || 'Sem descrição.'}</p>
        
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
    // Logic to enable crosshair cursor and wait for click
    if (!map) return;

    // Close modal momentarily
    const modalEl = document.getElementById('modalNovoPonto');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();

    Swal.fire({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        icon: 'info',
        title: 'Clique no mapa para marcar'
    });

    const container = document.getElementById('map');
    container.classList.add('cursor-crosshair');

    map.once('click', function (e) {
        document.getElementById('lat').value = e.latlng.lat.toFixed(6);
        document.getElementById('lng').value = e.latlng.lng.toFixed(6);
        container.classList.remove('cursor-crosshair');
        modal.show();
    });
}
