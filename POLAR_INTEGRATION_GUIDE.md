# Polar.sh Paywall Integration Guide

## Overview
The LOHA Dating Coach now integrates with Polar.sh to provide a paywall after 6 free messages. Users can purchase unlimited access for a one-time payment of $2.95.

## Configuration

### Environment Variables
The following environment variables are configured (can be overridden):

```bash
POLAR_ACCESS_TOKEN=polar_oat_QBoGv8YGoNQwMIWdEMLBk9aXYTZSN5WPVOoWt2ENnmy
POLAR_WEBHOOK_SECRET=polar_whs_h2512lJjXrj0R8hxR2q2JNZlij8MpxpimKfzq41AcrW
POLAR_PRODUCT_ID=26111cdd-7cf0-49b3-a068-61eede577684
POLAR_SUCCESS_URL=https://lohacoachpilot.onrender.com/success?checkout_id={CHECKOUT_ID}
```

## How It Works

### 1. Message Tracking
- Each user session has a unique `session_id`
- Messages are counted automatically
- After 6 messages, the paywall is triggered

### 2. Paywall Trigger
- When a user sends their 7th message, the system:
  - Creates a Polar checkout session
  - Returns a paywall message with a payment button
  - Pauses the conversation until payment is completed

### 3. Payment Flow
- User clicks "Continue Conversation - $2.95" button
- Redirected to Polar.sh secure checkout
- After successful payment, user is redirected to `/success?checkout_id={session_id}`
- The session is marked as paid
- User can return to the chat and continue with full access

### 4. Session Continuity
- All conversation history is preserved
- User returns to the exact conversation state
- No data is lost during the payment process
- Paid sessions have unlimited message access

## Integration Points

### Backend (`app.py`)
- **Polar Integration Module**: `polar_integration.py` handles all Polar.sh API interactions
- **Chat Endpoint**: Modified `/api/chat` to check payment status and trigger paywall
- **Webhook Endpoint**: `/api/polar/webhook` receives payment confirmations
- **Success Page**: `/success` route handles post-payment redirect

### Frontend (`templates/index.html`)
- **Paywall Display**: New `displayPaywall()` function shows payment UI
- **Styling**: Custom CSS for paywall message and payment button
- **Message Handling**: Updated `sendMessage()` to handle paywall responses

### Success Page (`templates/success.html`)
- Displays payment confirmation
- Provides "Return to Conversation" button
- Shows session information

## File Structure

```
loha-dating-coach-v2/
├── app.py                          # Main Flask app (modified)
├── polar_integration.py            # Polar.sh integration module (new)
├── templates/
│   ├── index.html                  # Main chat interface (modified)
│   └── success.html                # Payment success page (new)
├── requirements.txt                # Dependencies (unchanged)
└── POLAR_INTEGRATION_GUIDE.md      # This file
```

## API Endpoints

### POST /api/chat
Handle chat messages with paywall logic.

**Request:**
```json
{
  "session_id": "user-123",
  "message": "Hello!"
}
```

**Response (Normal):**
```json
{
  "success": true,
  "message": "AI response here"
}
```

**Response (Paywall Triggered):**
```json
{
  "success": true,
  "paywall_required": true,
  "message": "Paywall message...",
  "checkout_url": "https://polar.sh/checkout/...",
  "message_count": 6
}
```

### POST /api/polar/webhook
Handle Polar webhook events.

**Events:**
- `checkout.completed`: Marks session as paid

### GET /success
Success page after payment.

**Query Parameters:**
- `checkout_id`: Session ID

## Deployment

### Environment Setup
Set the following environment variables in your deployment environment:

```bash
export POLAR_ACCESS_TOKEN=polar_oat_QBoGv8YGoNQwMIWdEMLBk9aXYTZSN5WPVOoWt2ENnmy
export POLAR_WEBHOOK_SECRET=polar_whs_h2512lJjXrj0R8hxR2q2JNZlij8MpxpimKfzq41AcrW
export POLAR_PRODUCT_ID=26111cdd-7cf0-49b3-a068-61eede577684
export POLAR_SUCCESS_URL=https://lohacoachpilot.onrender.com/success?checkout_id={CHECKOUT_ID}
```

### Render Deployment
The app is configured to deploy to Render at: `https://lohacoachpilot.onrender.com`

1. Push code to your Git repository
2. Connect repository to Render
3. Set environment variables in Render dashboard
4. Deploy

### Webhook Configuration
Configure Polar webhook URL:
```
https://lohacoachpilot.onrender.com/api/polar/webhook
```

## Testing

### Local Testing
1. Set environment variables
2. Run the app: `python app.py`
3. Open browser to `http://localhost:9024`
4. Start a conversation and send 6 messages
5. On 7th message, paywall should appear
6. Test payment flow (use Polar test mode if available)

### Key Test Scenarios
- ✅ Messages count correctly
- ✅ Paywall triggers exactly after 6 messages
- ✅ Paywall UI displays correctly
- ✅ Payment button redirects to Polar checkout
- ✅ Success page loads after payment
- ✅ Session is marked as paid
- ✅ User can continue conversation after payment
- ✅ Conversation history is preserved
- ✅ Paid users have unlimited access

## Security Notes

1. **Webhook Verification**: In production, implement proper signature verification
2. **Session Security**: Use secure session management
3. **Payment Verification**: Double-check payment status with Polar API
4. **Rate Limiting**: Consider adding rate limiting to prevent abuse

## Troubleshooting

### Paywall Not Triggering
- Check message counter is incrementing
- Verify `PAYWALL_MESSAGE_LIMIT` is set to 6
- Check console for JavaScript errors

### Payment Not Processing
- Verify Polar API credentials
- Check webhook URL is correct
- Verify product ID matches
- Check Polar dashboard for transaction logs

### Session Lost After Payment
- Ensure `session_id` is properly passed through checkout URL
- Verify success page marks session as paid
- Check that `paid_sessions` set is maintained (consider Redis for production)

## Future Enhancements

- [ ] Add Redis for session persistence across restarts
- [ ] Implement proper webhook signature verification
- [ ] Add analytics for payment conversion
- [ ] Support for multiple payment tiers
- [ ] Add subscription model option
- [ ] Implement grace period or trial extension
- [ ] Add refund handling logic

## Support

For issues or questions about the Polar integration:
- Check Polar.sh documentation: https://docs.polar.sh/
- Review this integration guide
- Check server logs for error messages