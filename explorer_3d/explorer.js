/* PayQuant 3D Quantum Diamond Explorer - explorer.js (public client)
 * Renders each block's public 3D diamond geometry from diamonds.json.
 * Geometry/lighting/colors are derived from public block hashes only.
 */
"use strict";

var diamonds = [], idx = 0;
var renderer = null, scene = null, camera = null, controls = null;
var current = null, movingLight = null;

function $(id) { return document.getElementById(id); }

function toast(msg) {
  var t = $('toast');
  if (!t) return;
  t.textContent = msg;
  t.style.opacity = 1;
  setTimeout(function () { t.style.opacity = 0; }, 2600);
}

function hexToRgb(h) {
  h = String(h || '#8B5CF6').replace('#', '');
  return [parseInt(h.substr(0, 2), 16) / 255,
          parseInt(h.substr(2, 2), 16) / 255,
          parseInt(h.substr(4, 2), 16) / 255];
}

function colorFromVal(v) {
  if (Array.isArray(v)) { return hexToRgb(rgbToHex(v)); }
  return hexToRgb(v || '#8B5CF6');
}
function rgbToHex(arr) {
  function cl(x) { return Math.max(0, Math.min(255, Math.round(x * 255))); }
  return '#' + [cl(arr[0]), cl(arr[1]), cl(arr[2])]
    .map(function (x) { return x.toString(16).padStart(2, '0'); }).join('');
}

function init3D() {
  renderer = new THREE.WebGLRenderer({ canvas: $('c3d'), antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(3.1, 2.2, 4.0);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 1.8;

  window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
  renderer.setAnimationLoop(animate);
  loadData();
}

function animate() {
  controls.update();
  if (current) current.rotation.y += 0.004;
  if (movingLight) {
    var t = Date.now() * 0.0006;
    movingLight.position.set(6 * Math.cos(t), 3, 6 * Math.sin(t));
  }
  renderer.render(scene, camera);
}

function buildDiamond(rec) {
  var g = rec.geometry_3d || { vertices: [], faces: [] };
  var colors = rec.colors || ['#8B5CF6'];
  var verts = g.vertices.map(function (v) { return new THREE.Vector3(v[0], v[1], v[2]); });
  var geom = new THREE.BufferGeometry();
  var pos = [], col = [];
  (g.faces || []).forEach(function (f) {
    for (var i = 0; i < 3; i++) {
      var v = verts[f[i]] || new THREE.Vector3();
      pos.push(v.x, v.y, v.z);
      var c = hexToRgb(colors[(f[0] + i) % colors.length]);
      col.push(c[0], c[1], c[2]);
    }
  });
  geom.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geom.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  geom.computeVertexNormals();
  var mat = new THREE.MeshPhongMaterial({
    vertexColors: true, shininess: 110, specular: 0xffffff,
    transparent: true, opacity: 0.96, emissive: 0x12061f
  });
  return new THREE.Mesh(geom, mat);
}

function setLights(d) {
  scene.children.slice().forEach(function (o) {
    if (o && (o.isAmbientLight || o.isDirectionalLight || o.isPointLight)) scene.remove(o);
  });
  var lig = d.lighting || {
    ambient: { intensity: 0.35 },
    primary: { position: [1, 1, 1], color: [1, 1, 1], intensity: 0.9 },
    secondary: { position: [-1, 1, 1], color: [0.4, 0.6, 1], intensity: 0.4 }
  };
  scene.add(new THREE.AmbientLight(0x8899ff, (lig.ambient.intensity || 0.35) * 1.8));

  var p = lig.primary || {};
  var d1 = new THREE.DirectionalLight(0xffffff, p.intensity || 0.9);
  var pp = p.position || [1, 1, 1];
  d1.position.set(pp[0] * 6, pp[1] * 6, pp[2] * 6);
  scene.add(d1);

  var s = lig.secondary || {};
  var d2 = new THREE.DirectionalLight(0x88aaff, s.intensity || 0.4);
  var sp = s.position || [-1, 1, 1];
  d2.position.set(sp[0] * 6, sp[1] * 6, sp[2] * 6);
  scene.add(d2);
  movingLight = d1;
}

function showBlock(rec) {
  if (!rec) return;
  if (current) scene.remove(current);
  current = buildDiamond(rec);
  scene.add(current);
  setLights(rec);
  document.getElementById('blabel').textContent = 'Block #' + (rec.height || '?');
  document.getElementById('meta').innerHTML =
    '<div>footprint: <span style="color:#8BD8FC">' + (rec.quantum_footprint || '').slice(0, 24) + '…</span></div>' +
    '<div>hash: ' + (rec.hash || '').slice(0, 24) + '…</div>' +
    '<div>miner: ' + (rec.miner || '—') + '</div>' +
    '<div>facets: ' + (rec.geometry_3d ? rec.geometry_3d.faces.length : 0) +
    ' · colors: ' + (rec.colors ? rec.colors.length : 0) + '</div>';
}

function cycle(dir) {
  if (!diamonds.length) return;
  idx = (idx + dir + diamonds.length) % diamonds.length;
  showBlock(diamonds[idx]);
  toast('Quantum diamond · Block ' + diamonds[idx].height);
}

function resetView() {
  camera.position.set(3.2, 2.2, 4.0);
  controls.target.set(0, 0, 0);
  controls.autoRotate = !controls.autoRotate;
}

function renderThumbs() {
  var box = $('gallery');
  if (!box) return;
  box.innerHTML = '';
  diamonds.slice(0, 400).forEach(function (rec, i) {
    var el = document.createElement('div');
    el.className = 'thumb';
    el.innerHTML = '<b>#' + rec.height + '</b><span style="flex:1">' +
      (rec.quantum_footprint || '').slice(0, 10) + '…</span>';
    (function (bi) {
      el.onclick = function () { toggleGallery(false); showBlock(diamonds[bi]); toast('Block ' + diamonds[bi].height); };
    })(i);
    box.appendChild(el);
  });
}

function toggleGallery(force) {
  var box = $('gallery');
  var show = (typeof force === 'boolean') ? force : (box.style.display === 'none');
  box.style.display = show ? 'block' : 'none';
}

function loadData() {
  var m = /#(\d+)/.exec(location.hash || '');
  if (m) idx = parseInt(m[1], 10);
  var meta = $('meta');
  fetch('diamonds.json').then(function (r) { return r.json(); }).then(function (doc) {
    diamonds = doc.diamonds || [];
    if (!diamonds.length) throw new Error('no diamonds in json');
    renderThumbs();
    showBlock(diamonds[idx % diamonds.length]);
  }).catch(function () {
    if (meta) meta.textContent = 'diamonds.json not found next to this page.';
  });
}

document.addEventListener('DOMContentLoaded', init3D);
window.showBlock = showBlock;
window.cycle = cycle;
window.resetView = resetView;
window.toggleGallery = toggleGallery;