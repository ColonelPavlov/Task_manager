// ======================== ЗАДАЧИ (CRUD) ========================
function showAddTask() {
  editingTaskId = null;
  chosenTagId = null;
  document.getElementById('taskModalTitle').textContent = '➕ Новая задача';
  document.getElementById('taskTitle').value = '';
  document.getElementById('taskDescription').value = '';
  document.getElementById('taskDeadline').value = '';
  document.getElementById('taskPriority').value = 'medium';
  document.getElementById('taskProject').value = '';
  renderModalTags();
  taskModal.show();
}

function openEditTaskModal(taskId) {
  const task = tasks.find(t => t.task_id === taskId);
  if (!task) return;
  editingTaskId = taskId;
  chosenTagId = task.tag_id || null;
  document.getElementById('taskModalTitle').textContent = '✏️ Редактировать задачу';
  document.getElementById('taskTitle').value = task.task_number;
  document.getElementById('taskDescription').value = task.description || '';
  document.getElementById('taskDeadline').value = task.deadline ? task.deadline.slice(0, 16) : '';
  document.getElementById('taskPriority').value = task.priority || 'medium';
  document.getElementById('taskProject').value = task.project_id || '';
  renderModalTags();
  taskModal.show();
}

async function saveTask() {
  const title = document.getElementById('taskTitle').value.trim();
  if (!title) { alert('Введите название задачи'); return; }

  const projectIdRaw = document.getElementById('taskProject').value;
  const project_id = projectIdRaw ? Number(projectIdRaw) : null;
  const deadlineRaw = document.getElementById('taskDeadline').value;
  const deadline = deadlineRaw ? new Date(deadlineRaw).toISOString() : null;
  const priority = document.getElementById('taskPriority').value;
  const description = document.getElementById('taskDescription').value;
  const tag_id = chosenTagId ? Number(chosenTagId) : null;

  const taskData = {
    task_number: title,
    description,
    deadline,
    priority,
    project_id,
    tag_id,
    status: editingTaskId ? (tasks.find(t => t.task_id === editingTaskId)?.status || 'todo') : 'todo'
  };

  try {
    let result;
    if (editingTaskId) {
      result = await apiRequest(`/tasks/${editingTaskId}`, 'PUT', taskData);
      const updatedTask = result.data?.task;
      if (updatedTask) {
        const index = tasks.findIndex(t => t.task_id === editingTaskId);
        if (index !== -1) tasks[index] = updatedTask;
      }
    } else {
      result = await apiRequest('/tasks', 'POST', taskData);
      const newTask = result.data?.task;
      if (newTask) tasks.push(newTask);
    }
    renderKanban();
    refreshStats();
    taskModal.hide();
  } catch (err) {
    alert('Ошибка сохранения задачи: ' + err.message);
  }
}

async function deleteTask(taskId) {
  if (!confirm('Удалить задачу навсегда?')) return;
  try {
    await apiRequest(`/tasks/${taskId}`, 'DELETE');
    tasks = tasks.filter(t => t.task_id !== taskId);
    renderKanban();
    refreshStats();
  } catch (err) {
    alert('Ошибка удаления задачи: ' + err.message);
  }
}
