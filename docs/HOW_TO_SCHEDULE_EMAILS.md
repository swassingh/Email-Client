# How to Schedule Emails

This guide explains how to schedule emails for future sending in NovaMail POC.

## Scheduling an Email

### Step-by-Step Instructions

1. **Open the Compose Form**
   - Click the floating "+" button in the bottom-right corner

2. **Fill in Email Details**
   - Enter recipient email address
   - Enter subject
   - Write your message

3. **Enable Scheduling**
   - Check the **"Schedule Send"** checkbox
   - A date/time picker will appear

4. **Select Date and Time**
   - Click the date/time picker
   - Choose a future date and time
   - The picker prevents selecting past dates/times

5. **Schedule the Email**
   - Click the **"Schedule Send"** button (appears when checkbox is checked)
   - The email will be saved with `email_type: "scheduled"`
   - You'll see a confirmation message with the scheduled time

6. **View Scheduled Emails**
   - Go to the **"Scheduled"** tab to see all scheduled emails
   - Scheduled emails show the scheduled date/time in the email list

## Features

### Validation
- **Future Date Required**: You cannot schedule emails for past dates/times
- **Required Fields**: Recipient, Subject, and Message must be filled
- **Visual Indicator**: Scheduled emails display the scheduled date/time

### Email Status
- Scheduled emails have `email_type: "scheduled"`
- They appear in the "Scheduled" tab
- The scheduled date/time is stored in `scheduled_at` field (ISO format)

## Example

1. Click compose button (+)
2. Fill in:
   - To: `user@example.com`
   - Subject: `Meeting Reminder`
   - Message: `Don't forget about our meeting tomorrow!`
3. Check "Schedule Send" checkbox
4. Select date/time: `2026-03-01 14:00`
5. Click "Schedule Send"
6. Email is saved and appears in Scheduled tab

## API Usage

You can also schedule emails via the API:

```bash
POST /api/emails
Content-Type: application/json

{
  "sender": "pm@novamail.dev",
  "recipient": "user@example.com",
  "subject": "Scheduled Email",
  "body": "This email is scheduled",
  "email_type": "scheduled",
  "scheduled_at": "2026-03-01T14:00:00.000Z"
}
```

**Note**: The `scheduled_at` field must be an ISO 8601 datetime string in UTC.

## Notes

- Scheduled emails are stored but not automatically sent (this is a POC)
- In a production system, a background job would check scheduled emails and send them at the appropriate time
- You can view scheduled emails in the "Scheduled" tab
- Scheduled emails can be moved to trash like other emails

