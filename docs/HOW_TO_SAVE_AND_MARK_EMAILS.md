# How to Save and Mark Emails by Type

This guide explains how to save emails as drafts and mark existing emails with different types in NovaMail POC.

## Saving Emails as Drafts

### Method 1: Using the Compose Form

1. **Open the Compose Form**
   - Click the floating "+" button in the bottom-right corner

2. **Fill in Email Details**
   - Enter recipient (optional for drafts)
   - Enter subject (optional for drafts)
   - Write your message

3. **Save as Draft**
   - Click the **"Save Draft"** button (left side of form actions)
   - The email will be saved with `email_type: "draft"`
   - You can find it later in the **"Draft"** tab

**Note**: At least a subject or message body is required to save a draft.

### Method 2: Via API

```bash
POST /api/emails
Content-Type: application/json

{
  "sender": "pm@novamail.dev",
  "recipient": "user@example.com",
  "subject": "Draft Email",
  "body": "This is a draft",
  "email_type": "draft"
}
```

## Marking Existing Emails

### Using the Email Detail View

1. **Open an Email**
   - Click on any email in your inbox/list to open the detail view

2. **Use Action Buttons**
   At the bottom of the email detail modal, you'll see action buttons:
   
   - **Move to Inbox**: Changes email type to `inbox`
   - **Mark as Spam**: Changes email type to `spam`
   - **Mark as Junk**: Changes email type to `junk`
   - **Move to Trash**: Changes email type to `trash` (with confirmation)

3. **Result**
   - The email will be moved to the corresponding tab
   - The inbox will refresh automatically

### Via API

Update an email's type using PATCH:

```bash
PATCH /api/emails/{email_id}
Content-Type: application/json

{
  "email_type": "spam"
}
```

**Valid types**: `inbox`, `sent`, `draft`, `scheduled`, `spam`, `junk`, `trash`

## Email Type Actions Summary

| Action | Button | Email Type | Tab Location |
|--------|--------|------------|--------------|
| Save Draft | "Save Draft" | `draft` | Draft tab |
| Move to Inbox | "Move to Inbox" | `inbox` | Inbox tab |
| Mark as Spam | "Mark as Spam" | `spam` | Spam tab |
| Mark as Junk | "Mark as Junk" | `junk` | Junk tab |
| Move to Trash | "Move to Trash" | `trash` | Trash tab |

## Examples

### Example 1: Save a Draft

1. Click compose button (+)
2. Enter subject: "Meeting Notes"
3. Enter body: "Need to discuss..."
4. Click "Save Draft"
5. Find it in the Draft tab

### Example 2: Mark Email as Spam

1. Click on an email to open it
2. Click "Mark as Spam" button
3. Email moves to Spam tab automatically

### Example 3: Move Email to Trash

1. Open an email
2. Click "Move to Trash"
3. Confirm the action
4. Email moves to Trash tab

## Notes

- **Drafts** can be edited and sent later (future feature)
- **Trash** emails can be restored by moving them back to inbox
- **Spam** and **Junk** emails are filtered from the main inbox
- All type changes are immediate and persist in the database
- The inbox automatically refreshes after any type change

