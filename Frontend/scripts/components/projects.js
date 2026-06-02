// ======================== ПРОЕКТЫ ========================
function renderProjects() {
  const container = document.getElementById('projectList');
  if (!container) return;
  let html = `<div class="project-item p-2 rounded mb-1 ${currentProjectId === null ? 'bg-success' : 'bg-secondary bg-opacity-25'}" onclick="selectProject(null)">📋 Все задачи</div>`;
  for (let p of projects) {
    html += `<div class="project-item p-2 rounded mb-1 d-flex justify-content-between align-items-center ${currentProjectId === p.project_id ? 'bg-success' : 'bg-secondary bg-opacity-25'}" onclick="selectProject(${p.project_id})">
      <span>📁 ${escapeHtml(p.name)}</span>
      <button class="btn btn-sm btn-danger rounded-pill" onclick="event.stopPropagation(); deleteProject(${p.project_id})">🗑️</button>
    </div>`;
  }
  container.innerHTML = html;
}

function selectProject(projectId) {
  currentProjectId = projectId;
  const project = projects.find(p => p.project_id === projectId);
  document.getElementById('currentProjectTitle').innerHTML = projectId ? `📁 ${escapeHtml(project.name)}` : '📋 Все задачи';
  renderProjects();
  renderKanban();
}

async function addProject() {
  const input = document.getElementById('newProjectName');
  const name = input.value.trim();
  if (!name) { alert('Введите название проекта!'); return; }
  try {
    const result = await apiRequest('/projects', 'POST', { name });
    projects.push({ project_id: result.project_id, name });
    renderProjects();
    updateProjectSelect();
    input.value = '';
  } catch (err) {
    alert('Ошибка создания проекта: ' + err.message);
  }
}

async function deleteProject(projectId) {
  const project = projects.find(p => p.project_id === projectId);
  if (!project) return;
  if (!confirm(`Удалить проект "${project.name}"? Все задачи останутся без проекта.`)) return;
  try {
    await apiRequest(`/projects/${encodeURIComponent(project.name)}`, 'DELETE');
    projects = projects.filter(p => p.project_id !== projectId);
    if (currentProjectId === projectId) currentProjectId = null;
    const tasksData = await apiRequest('/tasks', 'GET');
    tasks = tasksData.tasks || [];
    renderProjects();
    updateProjectSelect();
    renderKanban();
  } catch (err) {
    alert('Ошибка удаления проекта: ' + err.message);
  }
}

function updateProjectSelect() {
  const select = document.getElementById('taskProject');
  if (!select) return;
  let options = '<option value="">Без проекта</option>';
  for (let p of projects) options += `<option value="${p.project_id}">${escapeHtml(p.name)}</option>`;
  select.innerHTML = options;
}
