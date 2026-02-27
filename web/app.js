const form = document.getElementById('compose-form');
const recipientFilter = document.getElementById('recipient-filter');
const refreshBtn = document.getElementById('refresh-btn');
const sendArchEmailBtn = document.getElementById('send-arch-email-btn');
const sendStatus = document.getElementById('send-status');
const laneFocus = document.getElementById('lane-focus');
const laneQuick = document.getElementById('lane-quick');
const laneFYI = document.getElementById('lane-fyi');

function laneForEmail(email) {
  const text = `${email.subject} ${email.body}`.toLowerCase();
  if (text.includes('urgent') || text.includes('asap') || text.includes('review') || text.includes('manager')) return 'focus';
  if ((email.body || '').length < 120 || text.includes('quick') || text.includes('confirm')) return 'quick';
  return 'fyi';
}

function renderEmail(email) {
  const li = document.createElement('li');
  li.className = 'mail-card';
  li.innerHTML = `
    <div class="mail-top">
      <span class="subject">${email.subject}</span>
      <span class="timestamp">${new Date(email.created_at).toLocaleString()}</span>
    </div>
    <div class="meta">${email.sender} → ${email.recipient}</div>
    <p>${email.body}</p>
  `;
  return li;
}

function clearLanes() {
  laneFocus.innerHTML = '';
  laneQuick.innerHTML = '';
  laneFYI.innerHTML = '';
}

async function fetchInbox() {
  const recipient = encodeURIComponent(recipientFilter.value.trim());
  const response = await fetch(`/api/emails?recipient=${recipient}`);
  const emails = await response.json();

  clearLanes();
  for (const email of emails) {
    const lane = laneForEmail(email);
    const card = renderEmail(email);
    if (lane === 'focus') laneFocus.appendChild(card);
    else if (lane === 'quick') laneQuick.appendChild(card);
    else laneFYI.appendChild(card);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  const response = await fetch('/api/emails', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    alert(error.error || 'Failed to send email');
    return;
  }

  form.reset();
  await fetchInbox();
});

sendArchEmailBtn.addEventListener('click', async () => {
  sendStatus.textContent = 'Sending via SMTP...';
  const response = await fetch('/api/send-architecture-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recipient: 'Swastik.Singh@gmail.com' }),
  });

  const result = await response.json();
  if (!response.ok) {
    sendStatus.textContent = result.error || 'Failed to send architecture email';
    return;
  }

  sendStatus.textContent = result.message;
  recipientFilter.value = 'Swastik.Singh@gmail.com';
  await fetchInbox();
});

refreshBtn.addEventListener('click', fetchInbox);
fetchInbox();
