// ======================== ТЕГИ ========================
function renderAllTags() {
  const container = document.getElementById('allTagsList');
  if (!container) return;
  let html = '';
  for (let tag of allTags) {
    html += `<div class="tag-item" style="background-color: ${tag.color}">${escapeHtml(tag.name)}<span class="remove-tag" onclick="deleteTag(${tag.tag_id})">×</span></div>`;
  }
  container.innerHTML = html;
}

function renderModalTags() {
  const container = document.getElementById('modalTagsList');
  if (!container) return;
  let html = '';
  for (let tag of allTags) {
    const isSelected = chosenTagId === tag.tag_id;
    html += `<div class="tag-item ${isSelected ? 'selected' : ''}" style="background-color: ${tag.color}" onclick="toggleTag(${tag.tag_id})">${escapeHtml(tag.name)} ${isSelected ? '✓' : ''}</div>`;
  }
  container.innerHTML = html;
}

function toggleTag(tagId) {
  chosenTagId = chosenTagId === tagId ? null : tagId;
  renderModalTags();
}

async function addNewTagFromModal() {
  const name = document.getElementById('newTagName').value.trim();
  const color = document.getElementById('newTagColor').value;
  if (!name) { alert('Введите название тега'); return; }
  try {
    const result = await apiRequest('/tags', 'POST', { name, color });
    const newTag = { tag_id: result.tag.id, name: result.tag.name, color: result.tag.color };
    allTags.push(newTag);
    renderAllTags();
    renderModalTags();
    document.getElementById('newTagName').value = '';
  } catch (err) {
    alert('Ошибка создания тега: ' + err.message);
  }
}

async function deleteTag(tagId) {
  try {
    await apiRequest(`/tags/${tagId}`, 'DELETE');
    allTags = allTags.filter(t => t.tag_id !== tagId);
    if (chosenTagId === tagId) chosenTagId = null;
    const tasksData = await apiRequest('/tasks', 'GET');
    tasks = tasksData.tasks || [];
    renderAllTags();
    renderKanban();
  } catch (err) {
    alert('Ошибка удаления тега: ' + err.message);
  }
}
