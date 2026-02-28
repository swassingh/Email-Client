const form = document.getElementById('compose-form');
const inbox = document.getElementById('inbox');
const recipientFilter = document.getElementById('recipient-filter');
const refreshBtn = document.getElementById('refresh-btn');
const composeBtn = document.getElementById('compose-btn');
const composeModal = document.getElementById('compose-modal');
const closeModal = document.getElementById('close-modal');
const cancelBtn = document.getElementById('cancel-btn');
const emptyState = document.getElementById('empty-state');
const tabButtons = document.querySelectorAll('.tab-btn');
const emailDetailModal = document.getElementById('email-detail-modal');
const closeDetailModal = document.getElementById('close-detail-modal');
const saveDraftBtn = document.getElementById('save-draft-btn');
const markInboxBtn = document.getElementById('mark-inbox-btn');
const markSpamBtn = document.getElementById('mark-spam-btn');
const markJunkBtn = document.getElementById('mark-junk-btn');
const markTrashBtn = document.getElementById('mark-trash-btn');
const scheduleCheckbox = document.getElementById('schedule-checkbox');
const scheduleDateTime = document.getElementById('schedule-datetime');
const scheduleSendBtn = document.getElementById('schedule-send-btn');

let currentTab = 'inbox';
let currentEmail = null; // Store currently viewed email
const defaultSender = 'pm@novamail.dev';
const defaultRecipient = 'Swastik.Singh@gmail.com';

// Automatic PM Action - runs once on page load
async function sendArchitectureEmailOnce() {
  const hasSent = localStorage.getItem('pmArchEmailSent');
  if (hasSent === 'true') {
    return; // Already sent, skip
  }

  try {
    const res = await fetch('/api/send-architecture-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient: defaultRecipient }),
    });

    if (res.ok) {
      localStorage.setItem('pmArchEmailSent', 'true');
      // Refresh inbox to show the new email
      await fetchInbox();
    }
  } catch (error) {
    console.error('Failed to send architecture email:', error);
  }
}

async function fetchInbox() {
  try {
    let url = '/api/emails';
    
    if (currentTab === 'all') {
      // All emails - no filter
      url = '/api/emails';
    } else {
      // Filter by email type
      url += `?type=${encodeURIComponent(currentTab)}`;
    }
    
    const res = await fetch(url);
    const data = await res.json();

    inbox.innerHTML = '';
    
    if (data.length === 0) {
      emptyState.classList.add('visible');
      return;
    }
    
    emptyState.classList.remove('visible');
    
    for (const email of data) {
      const li = document.createElement('li');
      li.dataset.emailId = email.id;
      
      // Determine if this is sent or received based on email type
      const emailType = email.email_type || 'inbox';
      const isSent = emailType === 'sent' || email.sender.toLowerCase() === defaultSender.toLowerCase();
      const otherParty = isSent ? email.recipient : email.sender;
      
      // Add type badge
      const typeBadge = emailType !== 'inbox' && emailType !== 'sent' ? 
        `<span class="email-type-badge email-type-${emailType}">${emailType}</span>` : '';
      
      li.innerHTML = `
        <div class="email-header">
          <div class="email-subject">${escapeHtml(email.subject)}</div>
          ${typeBadge}
        </div>
        <div class="email-meta">
          <span>${isSent ? 'To' : 'From'}: ${escapeHtml(otherParty)}</span>
        </div>
        <div class="email-body">${escapeHtml(email.body.substring(0, 150))}${email.body.length > 150 ? '...' : ''}</div>
        <div class="email-date">
          ${new Date(email.created_at).toLocaleString()}
          ${email.scheduled_at ? `<br><span style="color: var(--primary-color); font-weight: 500;">Scheduled: ${new Date(email.scheduled_at).toLocaleString()}</span>` : ''}
        </div>
      `;
      
      // Make email clickable
      li.addEventListener('click', () => openEmailDetail(email));
      inbox.appendChild(li);
    }
  } catch (error) {
    console.error('Failed to fetch inbox:', error);
    emptyState.classList.add('visible');
  }
}

function openEmailDetail(email) {
  currentEmail = email; // Store for action buttons
  document.getElementById('detail-subject').textContent = email.subject;
  document.getElementById('detail-sender').textContent = email.sender;
  document.getElementById('detail-recipient').textContent = email.recipient;
  document.getElementById('detail-date').textContent = new Date(email.created_at).toLocaleString();
  const emailType = email.email_type || 'inbox';
  document.getElementById('detail-type').textContent = emailType.charAt(0).toUpperCase() + emailType.slice(1);
  document.getElementById('detail-body').textContent = email.body;
  
  // Show scheduled date if exists
  const scheduledRow = document.getElementById('detail-scheduled-row');
  if (email.scheduled_at) {
    scheduledRow.style.display = 'flex';
    document.getElementById('detail-scheduled').textContent = new Date(email.scheduled_at).toLocaleString();
  } else {
    scheduledRow.style.display = 'none';
  }
  
  // Hide action buttons for sent emails (except trash)
  const emailActions = document.querySelector('.email-actions');
  const isSent = emailType.toLowerCase() === 'sent';
  if (isSent) {
    // Hide all buttons except trash
    markInboxBtn.style.display = 'none';
    markSpamBtn.style.display = 'none';
    markJunkBtn.style.display = 'none';
    markTrashBtn.style.display = 'block'; // Keep trash visible
    emailActions.style.display = 'flex';
  } else {
    // Show all buttons for non-sent emails
    markInboxBtn.style.display = 'block';
    markSpamBtn.style.display = 'block';
    markJunkBtn.style.display = 'block';
    markTrashBtn.style.display = 'block';
    emailActions.style.display = 'flex';
  }
  
  emailDetailModal.classList.add('active');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Tab switching
tabButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    // Update active tab
    tabButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentTab = btn.dataset.tab;
    
    // Refresh inbox with new filter
    fetchInbox();
  });
});

// Email detail modal functionality
closeDetailModal.addEventListener('click', () => {
  emailDetailModal.classList.remove('active');
});

emailDetailModal.addEventListener('click', (e) => {
  if (e.target === emailDetailModal) {
    emailDetailModal.classList.remove('active');
  }
});

// Close detail modal with Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (emailDetailModal.classList.contains('active')) {
      emailDetailModal.classList.remove('active');
    } else if (composeModal.classList.contains('active')) {
      composeModal.classList.remove('active');
      form.reset();
    }
  }
});

// Compose modal functionality
composeBtn.addEventListener('click', () => {
  composeModal.classList.add('active');
  // Focus on recipient input (first editable field)
  setTimeout(() => {
    form.querySelector('input[name="recipient"]').focus();
  }, 100);
});

closeModal.addEventListener('click', () => {
  composeModal.classList.remove('active');
});

cancelBtn.addEventListener('click', () => {
  composeModal.classList.remove('active');
  form.reset();
  // Reset sender to default
  form.querySelector('input[name="sender"]').value = defaultSender;
  // Reset schedule checkbox
  scheduleCheckbox.checked = false;
  scheduleDateTime.style.display = 'none';
  scheduleSendBtn.style.display = 'none';
});

// Close modal when clicking outside
composeModal.addEventListener('click', (e) => {
  if (e.target === composeModal) {
    composeModal.classList.remove('active');
    form.reset();
    form.querySelector('input[name="sender"]').value = defaultSender;
    scheduleCheckbox.checked = false;
    scheduleDateTime.style.display = 'none';
    scheduleSendBtn.style.display = 'none';
  }
});

// Schedule checkbox toggle
scheduleCheckbox.addEventListener('change', () => {
  if (scheduleCheckbox.checked) {
    scheduleDateTime.style.display = 'block';
    scheduleSendBtn.style.display = 'block';
    // Set minimum date to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    scheduleDateTime.min = now.toISOString().slice(0, 16);
  } else {
    scheduleDateTime.style.display = 'none';
    scheduleSendBtn.style.display = 'none';
    scheduleDateTime.value = '';
  }
});

// Schedule Send functionality
scheduleSendBtn.addEventListener('click', async () => {
  const payload = Object.fromEntries(new FormData(form).entries());
  
  // Validate required fields
  if (!payload.recipient.trim() || !payload.subject.trim() || !payload.body.trim()) {
    alert('Please fill in all required fields (To, Subject, Message).');
    return;
  }
  
  // Validate scheduled datetime
  if (!scheduleDateTime.value) {
    alert('Please select a date and time for scheduling.');
    return;
  }
  
  const scheduledDate = new Date(scheduleDateTime.value);
  const now = new Date();
  
  if (scheduledDate <= now) {
    alert('Scheduled time must be in the future.');
    return;
  }
  
  // Convert to ISO string for backend
  payload.scheduled_at = scheduledDate.toISOString();
  payload.email_type = 'scheduled';
  
  try {
    const res = await fetch('/api/emails', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.error || 'Failed to schedule email');
      return;
    }

    alert(`Email scheduled for ${scheduledDate.toLocaleString()}`);
    form.reset();
    form.querySelector('input[name="sender"]').value = defaultSender;
    scheduleCheckbox.checked = false;
    scheduleDateTime.style.display = 'none';
    scheduleSendBtn.style.display = 'none';
    composeModal.classList.remove('active');
    await fetchInbox();
  } catch (error) {
    console.error('Failed to schedule email:', error);
    alert('Failed to schedule email. Please try again.');
  }
});

// Save Draft functionality
saveDraftBtn.addEventListener('click', async () => {
  const payload = Object.fromEntries(new FormData(form).entries());
  
  // Validate at least subject or body exists
  if (!payload.subject.trim() && !payload.body.trim()) {
    alert('Please enter a subject or message to save as draft.');
    return;
  }
  
  // Set email_type to draft
  payload.email_type = 'draft';
  
  try {
    const res = await fetch('/api/emails', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.error || 'Failed to save draft');
      return;
    }

    alert('Draft saved successfully!');
    form.reset();
    form.querySelector('input[name="sender"]').value = defaultSender;
    composeModal.classList.remove('active');
    await fetchInbox();
  } catch (error) {
    console.error('Failed to save draft:', error);
    alert('Failed to save draft. Please try again.');
  }
});

// Form submission
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  
  try {
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
    // Reset sender to default
    form.querySelector('input[name="sender"]').value = defaultSender;
    composeModal.classList.remove('active');
    await fetchInbox();
  } catch (error) {
    console.error('Failed to send email:', error);
    alert('Failed to send email. Please try again.');
  }
});

// Email type change functionality
async function changeEmailType(emailId, newType) {
  try {
    const res = await fetch(`/api/emails/${emailId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email_type: newType }),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.error || 'Failed to update email');
      return;
    }

    // Close modal and refresh inbox
    emailDetailModal.classList.remove('active');
    await fetchInbox();
  } catch (error) {
    console.error('Failed to update email type:', error);
    alert('Failed to update email. Please try again.');
  }
}

// Action button handlers
markInboxBtn.addEventListener('click', () => {
  if (currentEmail) {
    changeEmailType(currentEmail.id, 'inbox');
  }
});

markSpamBtn.addEventListener('click', () => {
  if (currentEmail) {
    changeEmailType(currentEmail.id, 'spam');
  }
});

markJunkBtn.addEventListener('click', () => {
  if (currentEmail) {
    changeEmailType(currentEmail.id, 'junk');
  }
});

markTrashBtn.addEventListener('click', () => {
  if (currentEmail) {
    if (confirm('Move this email to trash?')) {
      changeEmailType(currentEmail.id, 'trash');
    }
  }
});

// Refresh button
refreshBtn.addEventListener('click', fetchInbox);

// Initialize: send PM email once, then fetch inbox
(async () => {
  await sendArchitectureEmailOnce();
  await fetchInbox();
})();
