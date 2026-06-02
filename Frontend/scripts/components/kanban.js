// ======================== КАНБАН ========================
function renderKanban() {
  const board = document.getElementById('kanbanBoard');
  if (!board) return;
  board.innerHTML = '';

  let filteredTasks = currentProjectId ? tasks.filter(t => t.project_id === currentProjectId) : tasks;
  filteredTasks = filteredTasks.filter(t => t && typeof t === 'object');

  for (let status of STATUSES) {
    const columnTasks = filteredTasks.filter(t => t.status === status);
    const column = document.createElement('div');
    column.className = 'kanban-column bg-murkoff-dark rounded-4 p-3';
    column.setAttribute('data-status', status);
    column.addEventListener('dragover', (e) => { e.preventDefault(); column.classList.add('drag-over'); });
    column.addEventListener('dragleave', () => column.classList.remove('drag-over'));
    column.addEventListener('drop', async (e) => {
      e.preventDefault();
      column.classList.remove('drag-over');
      if (dragId !== null) {
        await moveTask(dragId, status);
        dragId = null;
      }
    });
    column.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom border-success">
        <span class="fw-bold text-white fs-5">${STATUS_NAMES[status]}</span>
        <span class="badge bg-success rounded-pill px-3 py-2">${columnTasks.length}</span>
      </div>
      <div class="task-cards">
        ${columnTasks.map(task => renderTaskCard(task)).join('')}
      </div>
    `;
    board.appendChild(column);
  }

  document.querySelectorAll('.task-card').forEach(card => {
    card.setAttribute('draggable', 'true');
    card.addEventListener('dragstart', (e) => {
      const tid = card.getAttribute('data-task-id');
      dragId = tid ? parseInt(tid) : null;
      card.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    });
    card.addEventListener('dragend', () => card.classList.remove('dragging'));
  });
}

function renderTaskCard(task) {
  if (!task) return '';
  let priorityClass = 'priority-low', priorityText = '🟢 Низкий', borderColor = '#4caf50';
  if (task.priority === 'high')        { priorityClass = 'priority-high';   priorityText = '🔴 Высокий'; borderColor = '#f44336'; }
  else if (task.priority === 'medium') { priorityClass = 'priority-medium'; priorityText = '🟠 Средний'; borderColor = '#ff9800'; }

  const deadlineHtml = task.deadline ? `<div class="small text-danger mt-1">⏰ ${new Date(task.deadline).toLocaleString()}</div>` : '';
  let tagsHtml = '';
  if (task.tag_id) {
    const tag = allTags.find(t => t.tag_id === task.tag_id);
    if (tag) tagsHtml = `<span class="badge me-1" style="background-color: ${tag.color}">${escapeHtml(tag.name)}</span>`;
  }
  const project = projects.find(p => p.project_id === task.project_id);
  const projectName = project ? project.name : 'Без проекта';

  return `<div class="task-card card p-3 mb-2" data-task-id="${task.task_id}" style="border-left-color: ${borderColor}">
    <div class="fw-bold">${escapeHtml(task.task_number)}</div>
    <div class="small text-secondary">${escapeHtml(task.description || 'Нет описания')}</div>
    ${deadlineHtml}
    <div class="mt-1"><span class="badge ${priorityClass}">${priorityText}</span></div>
    <div class="mt-1">${tagsHtml}</div>
    <div class="small text-success mt-1">📁 ${escapeHtml(projectName)}</div>
    <div class="mt-2 d-flex gap-2">
      <button class="btn btn-sm btn-primary rounded-pill" onclick="event.stopPropagation(); openEditTaskModal(${task.task_id})">✏️ Править</button>
      <button class="btn btn-sm btn-danger rounded-pill" onclick="event.stopPropagation(); deleteTask(${task.task_id})">🗑️ Удалить</button>
    </div>
  </div>`;
}

async function moveTask(taskId, newStatus) {
  try {
    const result = await apiRequest(`/tasks/${taskId}`, 'PUT', { status: newStatus });
    const updatedTask = result.data?.task;
    if (updatedTask) {
      const index = tasks.findIndex(t => t.task_id === taskId);
      if (index !== -1) tasks[index] = updatedTask;
    }
    renderKanban();
    refreshStats();
  } catch (err) {
    alert('Ошибка перемещения задачи: ' + err.message);
  }
}
