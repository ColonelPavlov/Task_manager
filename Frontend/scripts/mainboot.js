// ======================== КОНФИГУРАЦИЯ ========================
const API_BASE_URL = 'http://localhost:8000/api';
const FLASK_BASE_URL = 'http://localhost:5001/api/v1/supporting';

// Глобальные переменные
let authToken = localStorage.getItem('authToken');
let agent = localStorage.getItem('agent');
let tasks = [];
let projects = [];
let allTags = [];
let currentProjectId = null;
let editingTaskId = null;
let chosenTagId = null;
let dragId = null;
let taskModal;
let prioritiesChart, statusesChart;

const STATUSES = ['todo', 'in_progress', 'done', 'on_hold'];
const STATUS_NAMES = {
  'todo': '📋 Нужно сделать',
  'in_progress': '⚙️ В процессе',
  'done': '✅ Готово',
  'on_hold': '⏸️ Отложено'
};

// ======================== АВТОРИЗАЦИЯ ========================
const urlParams = new URLSearchParams(window.location.search);
const urlToken = urlParams.get('access_token');
const urlAgent = urlParams.get('agent');
if (urlToken) localStorage.setItem('authToken', urlToken);
if (urlAgent) localStorage.setItem('agent', urlAgent);
authToken = localStorage.getItem('authToken');
agent = localStorage.getItem('agent');

if (!authToken || !agent) {
  window.location.href = 'logboot.html';
}

// ======================== API HELPER ========================
async function apiRequest(endpoint, method = 'GET', body = null) {
  const token = localStorage.getItem('authToken');
  if (!token) throw new Error('Нет токена');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  if (response.status === 401) {
    localStorage.removeItem('authToken');
    localStorage.removeItem('agent');
    window.location.href = 'logboot.html';
    throw new Error('Сессия истекла');
  }
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || data.message || 'Ошибка запроса');
  return data;
}

// ======================== ЗАГРУЗКА ВСЕХ ДАННЫХ ========================
async function loadData() {
  try {
    const tasksData = await apiRequest('/tasks', 'GET');
    tasks = tasksData.tasks || [];

    const projectsData = await apiRequest('/projects', 'GET');
    projects = projectsData.projects || [];

    const tagsData = await apiRequest('/tags', 'GET');
    allTags = (tagsData.tags || []).map(t => ({ tag_id: t.id, name: t.name, color: t.color }));

    const userData = await apiRequest(`/users/${encodeURIComponent(agent)}`, 'GET');
    const role = userData.role === 'admin' ? 'admin' : 'user';
    document.getElementById('userRoleBadge').textContent = role === 'admin' ? '👑 Администратор' : '👤 Пользователь';
    document.getElementById('profileRole').textContent = role === 'admin' ? 'Администратор' : 'Пользователь';

    renderProjects();
    renderAllTags();
    renderKanban();
    updateProjectSelect();
    refreshStats();
  } catch (error) {
    console.error('loadData error:', error);
    alert('Ошибка загрузки данных: ' + error.message);
  }
}

// ======================== СТАТИСТИКА (ПРОФИЛЬ) ========================
function refreshStats() {
  const active = tasks.filter(t => t.status !== 'done').length;
  const completed = tasks.filter(t => t.status === 'done').length;
  document.getElementById('profileStats').innerHTML = `${active} в работе, ${completed} выполнено`;
  document.getElementById('profileUser').innerText = agent;
}

// ======================== АНАЛИТИКА (FLASK) ========================
async function loadDashboardCharts() {
  try {
    const response = await fetch(`${FLASK_BASE_URL}/dashboard?agent=${encodeURIComponent(agent)}`);
    const result = await response.json();
    if (result.status === 'success') {
      const prioritiesCtx = document.getElementById('prioritiesChart').getContext('2d');
      const statusCtx = document.getElementById('statusesChart').getContext('2d');
      if (prioritiesChart) prioritiesChart.destroy();
      if (statusesChart) statusesChart.destroy();
      prioritiesChart = new Chart(prioritiesCtx, {
        type: 'bar',
        data: {
          labels: result.charts.task_priorities.labels,
          datasets: [{ label: 'Задачи', data: result.charts.task_priorities.datasets, backgroundColor: '#4a6741' }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
      });
      statusesChart = new Chart(statusCtx, {
        type: 'pie',
        data: {
          labels: result.charts.task_statuses.labels,
          datasets: [{ data: result.charts.task_statuses.datasets, backgroundColor: ['#4a6741', '#f44336', '#2196f3', '#ffeb3b'] }]
        }
      });
    }
  } catch (err) {
    console.error('Ошибка загрузки графиков:', err);
  }
}

// ======================== ВКЛАДКИ ========================
function switchTab(tabName) {
  document.getElementById('kanbanPage').style.display    = tabName === 'kanban'    ? 'block' : 'none';
  document.getElementById('profilePage').style.display   = tabName === 'profile'   ? 'block' : 'none';
  document.getElementById('analyticsPage').style.display = tabName === 'analytics' ? 'block' : 'none';
  if (tabName === 'analytics') loadDashboardCharts();
  if (tabName === 'profile')   refreshStats();
}

// ======================== ESCAPE HTML ========================
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]));
}

// ======================== ОБНОВЛЕНИЕ ТОКЕНА ========================
async function refreshToken() {
  const btn = document.getElementById('refreshTokenBtn');
  const msg = document.getElementById('refreshTokenMsg');
  btn.disabled = true;
  btn.textContent = '⏳ Обновление...';
  try {
    const data = await apiRequest(`/users/${encodeURIComponent(agent)}/refresh-token`, 'POST');
    localStorage.setItem('authToken', data.access_token);
    authToken = data.access_token;
    msg.className = 'mt-2 text-success';
    msg.textContent = '✅ Токен успешно обновлён! Сессия продлена на 12 часов.';
  } catch (error) {
    msg.className = 'mt-2 text-danger';
    msg.textContent = '❌ Ошибка: ' + error.message;
  } finally {
    msg.style.display = 'block';
    btn.disabled = false;
    btn.textContent = '🔄 Обновить токен';
  }
}

// ======================== ИНИЦИАЛИЗАЦИЯ ========================
document.addEventListener('DOMContentLoaded', () => {
  taskModal = new bootstrap.Modal(document.getElementById('taskModal'));
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active', 'bg-success'));
      this.classList.add('active', 'bg-success');
      switchTab(this.dataset.tab);
    });
  });
  document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('agent');
    window.location.href = 'logboot.html';
  });
  loadData();
});
