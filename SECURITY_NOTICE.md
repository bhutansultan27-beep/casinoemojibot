# ⚠️ IMPORTANT SECURITY NOTICE

## Token Rotation Required

Your Telegram bot token was temporarily exposed in development logs. Although the code now properly handles secrets and logging is sanitized, you need to rotate the token as a security precaution.

## Steps to Rotate Your Bot Token

1. **Open Telegram** and find **@BotFather**

2. **Send the command:**
   ```
   /revoke
   ```

3. **Select your bot** from the list

4. **Get your new token:**
   - After revoking, send `/token` to BotFather
   - Select your bot again
   - Copy the new token provided

5. **Update the Secret in Replit:**
   - Go to Tools > Secrets
   - Find `BOT_TOKEN`
   - Replace the old value with your new token
   - The bot will automatically restart with the new token

## What We Fixed

✅ Removed hardcoded token from `config.py`  
✅ Token now loads only from environment variables  
✅ Disabled httpx logging to prevent token exposure in logs  
✅ Deleted old logs containing the exposed token  
✅ Updated documentation with security best practices  

## Current Security Status

After you rotate the token:
- ✅ No secrets in code
- ✅ No secrets in logs
- ✅ Token managed via Replit Secrets
- ✅ Secure configuration pattern established

## Prevention

The bot is now configured to never expose secrets. All future runs will:
- Load BOT_TOKEN from environment only
- Keep httpx logging at WARNING level (no URL logging)
- Automatically save without exposing sensitive data

Please rotate your token now to complete the security fix.
