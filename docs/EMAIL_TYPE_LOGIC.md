# Email Type Logic Documentation

This document defines the logic and behavior for each email type in NovaMail POC.

## Email Types

### 1. **inbox** (Default for received emails)
- **Definition**: Emails received by the user
- **Logic**: 
  - Automatically assigned when recipient matches the default recipient (`Swastik.Singh@gmail.com`)
  - User's primary mailbox for incoming messages
- **Display**: Shown in "Inbox" tab
- **Auto-assignment**: When recipient is the default user's email

### 2. **sent** (Default for sent emails)
- **Definition**: Emails sent by the user
- **Logic**:
  - Automatically assigned when sender matches the default sender (`pm@novamail.dev`)
  - All emails composed and sent by the user
- **Display**: Shown in "Sent" tab
- **Auto-assignment**: When sender is the default user's email

### 3. **draft**
- **Definition**: Emails saved but not yet sent
- **Logic**:
  - Manually set when user saves a draft
  - Typically incomplete emails (may have missing recipient or subject)
  - Can be edited and sent later
- **Display**: Shown in "Draft" tab with draft badge
- **Auto-assignment**: Must be explicitly set via `email_type: "draft"` in API

### 4. **scheduled**
- **Definition**: Emails queued to be sent at a future date/time
- **Logic**:
  - Manually set when user schedules an email
  - Email is complete but not yet sent
  - Will be automatically moved to "sent" when scheduled time arrives
- **Display**: Shown in "Scheduled" tab with scheduled badge
- **Auto-assignment**: Must be explicitly set via `email_type: "scheduled"` in API

### 5. **spam**
- **Definition**: Emails identified as spam by filters or user
- **Logic**:
  - Automatically assigned by spam detection filters
  - Can be manually marked by user
  - Unwanted promotional or suspicious emails
- **Display**: Shown in "Spam" tab with spam badge
- **Auto-assignment**: Must be explicitly set via `email_type: "spam"` in API

### 6. **junk**
- **Definition**: Low-priority or unwanted emails (less severe than spam)
- **Logic**:
  - Manually marked by user
  - Low-priority newsletters, notifications, etc.
  - Similar to spam but less aggressive filtering
- **Display**: Shown in "Junk" tab with junk badge
- **Auto-assignment**: Must be explicitly set via `email_type: "junk"` in API

### 7. **trash**
- **Definition**: Deleted emails (soft delete)
- **Logic**:
  - Emails moved to trash by user
  - Can be restored or permanently deleted
  - Not shown in other tabs
- **Display**: Shown in "Trash" tab with trash badge
- **Auto-assignment**: Must be explicitly set via `email_type: "trash"` in API

## Auto-Assignment Rules

### Default Behavior (when `email_type` not provided):

1. **If sender = `pm@novamail.dev`** → `email_type = "sent"`
2. **If recipient = `Swastik.Singh@gmail.com`** → `email_type = "inbox"`
3. **Otherwise** → `email_type = "inbox"`

### Explicit Assignment:

Users can explicitly set `email_type` in the API payload:
```json
{
  "sender": "pm@novamail.dev",
  "recipient": "user@example.com",
  "subject": "My Email",
  "body": "Content",
  "email_type": "draft"  // Explicitly set
}
```

## Valid Email Types

The following are valid `email_type` values:
- `inbox`
- `sent`
- `draft`
- `scheduled`
- `spam`
- `junk`
- `trash`

Any other value will be ignored and auto-assignment logic will apply.

## API Examples

### Create a sent email (auto-assigned):
```bash
POST /api/emails
{
  "sender": "pm@novamail.dev",
  "recipient": "user@example.com",
  "subject": "Hello",
  "body": "Message"
}
# Result: email_type = "sent"
```

### Create an inbox email (auto-assigned):
```bash
POST /api/emails
{
  "sender": "other@example.com",
  "recipient": "Swastik.Singh@gmail.com",
  "subject": "Hello",
  "body": "Message"
}
# Result: email_type = "inbox"
```

### Create a draft (explicit):
```bash
POST /api/emails
{
  "sender": "pm@novamail.dev",
  "recipient": "user@example.com",
  "subject": "Draft",
  "body": "Unfinished message",
  "email_type": "draft"
}
# Result: email_type = "draft"
```

## Migration Logic

When loading old emails without `email_type` field:
- If sender matches default sender → `"sent"`
- If recipient matches default recipient → `"inbox"`
- Otherwise → `"inbox"`

