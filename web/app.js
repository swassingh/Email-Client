const form = document.getElementById('compose-form');
const inbox = document.getElementById('inbox');
const recipientFilter = document.getElementById('recipient-filter');
const refreshBtn = document.getElementById('refresh-btn');
const sendArchEmailBtn = document.getElementById('send-arch-email-btn');
const sendStatus = document.getElementById('send-status');

async function fetchInbox() {
  const recipient = encodeURIComponent(recipientFilter.value.trim());
  const res = await fetch(`/api/emails?recipient=${recipient}`);
  const data = await res.json();

  inbox.innerHTML = '';
  for (const email of data) {
    const li = document.createElement('li');
    li.innerHTML = `
      <div class="subject">${email.subject}</div>
      <div class="meta">From: ${email.sender} • To: ${email.recipient}</div>
      <p>${email.body}</p>
      <div class="meta">${new Date(email.created_at).toLocaleString()}</div>
    `;
    inbox.appendChild(li);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  const res = await fetch('/api/emails', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.error || 'Failed to send email');
    return;
  }

  form.reset();
  await fetchInbox();
});

sendArchEmailBtn.addEventListener('click', async () => {
  sendStatus.textContent = 'Sending...';
  const res = await fetch('/api/send-architecture-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recipient: 'Swastik.Singh@gmail.com' }),
  });

  if (!res.ok) {
    sendStatus.textContent = 'Failed to send architecture email.';
    return;
  }

  const data = await res.json();
  sendStatus.textContent = `Status: ${data.status} to ${data.email.recipient}`;
  recipientFilter.value = 'Swastik.Singh@gmail.com';
  await fetchInbox();
});

refreshBtn.addEventListener('click', fetchInbox);
fetchInbox();
