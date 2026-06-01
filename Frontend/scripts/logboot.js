let loginWin = document.getElementById('loginModal');
let regWin = document.getElementById('registerModal');
let loginModal = new bootstrap.Modal(loginWin);
let registerModal = new bootstrap.Modal(regWin);

function openLoginModal() {
  document.getElementById('loginError').style.display = 'none';
  document.getElementById('loginUsername').value = '';
  document.getElementById('loginPassword').value = '';
  loginModal.show();
}

function openRegisterModal() {
  document.getElementById('registerError').style.display = 'none';
  document.getElementById('registerSuccess').style.display = 'none';
  document.getElementById('regUsername').value = '';
  document.getElementById('regPassword').value = '';
  document.getElementById('regPasswordRepeat').value = '';
  registerModal.show();
}

async function login() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errorDiv = document.getElementById('loginError');

  if (!username || !password) {
    errorDiv.textContent = 'Заполните все поля!';
    errorDiv.style.display = 'block';
    return;
  }

  try {
    const response = await fetch('http://localhost:8000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok && data.access_token) {
      localStorage.setItem('authToken', data.access_token);
      localStorage.setItem('agent', username);
      console.log('[login] saved authToken=', localStorage.getItem('authToken'), 'len=', (localStorage.getItem('authToken')||'').length);
      console.log('[login] saved agent=', localStorage.getItem('agent'));

      // Передаём токен через querystring, чтобы исключить проблему localStorage между страницами
      const url = `mainboot.html?access_token=${encodeURIComponent(data.access_token)}&agent=${encodeURIComponent(username)}`;
      await new Promise(r => setTimeout(r, 0));
      window.location.href = url;
    } else {
      errorDiv.textContent = data.message || 'Неверный логин или пароль!';
      errorDiv.style.display = 'block';
    }
  } catch (error) {
    errorDiv.textContent = 'Ошибка подключения к серверу';
    errorDiv.style.display = 'block';
  }
}

async function register() {
  const username = document.getElementById('regUsername').value.trim();
  const password = document.getElementById('regPassword').value;
  const passwordRepeat = document.getElementById('regPasswordRepeat').value;
  const errorDiv = document.getElementById('registerError');
  const successDiv = document.getElementById('registerSuccess');

  if (!username || !password || !passwordRepeat) {
    errorDiv.textContent = 'Заполните все поля!';
    errorDiv.style.display = 'block';
    return;
  }

  if (password !== passwordRepeat) {
    errorDiv.textContent = 'Пароли не совпадают!';
    errorDiv.style.display = 'block';
    return;
  }

  try {
    const response = await fetch('http://localhost:8000/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
      successDiv.textContent = 'Регистрация успешна! Теперь войдите.';
      successDiv.style.display = 'block';
      setTimeout(() => {
        registerModal.hide();
        openLoginModal();
      }, 1500);
    } else {
      errorDiv.textContent = data.message || 'Ошибка регистрации';
      errorDiv.style.display = 'block';
    }
  } catch (error) {
    errorDiv.textContent = 'Ошибка подключения к серверу. Запусти бэкенд!';
    errorDiv.style.display = 'block';
  }
}
