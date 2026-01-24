# Polar.sh Paywall Deployment Checklist

## Pre-Deployment Checklist

### Environment Configuration ✅
- [x] Polar Access Token configured
- [x] Polar Webhook Secret configured
- [x] Polar Product ID configured
- [x] Success URL configured

### Code Integration ✅
- [x] `polar_integration.py` module created
- [x] `app.py` updated with paywall logic
- [x] `templates/index.html` updated with paywall UI
- [x] `templates/success.html` created
- [x] Message counter implemented (6 message limit)
- [x] Webhook endpoint added
- [x] Success page route added

### Testing ✅
- [x] Modules import successfully
- [x] Payment tracking works correctly
- [x] All routes registered properly
- [x] Flask app starts without errors
- [x] Paywall configuration verified

## Deployment Steps

### 1. Prepare Repository
```bash
# Navigate to project directory
cd loha-dating-coach-v2

# Verify all files are present
ls -la

# Check for new/modified files
git status
```

### 2. Commit Changes
```bash
# Add all new and modified files
git add app.py
git add polar_integration.py
git add templates/index.html
git add templates/success.html
git add POLAR_INTEGRATION_GUIDE.md
git add DEPLOYMENT_CHECKLIST.md
git add INTEGRATION_SUMMARY.md

# Commit with descriptive message
git commit -m "Integrate Polar.sh paywall - 6 free messages, then $2.95 payment"
```

### 3. Push to Git Repository
```bash
# Push to your repository
git push origin main
```

### 4. Configure Render Environment Variables

Set these environment variables in your Render dashboard:

```bash
# Polar Configuration
POLAR_ACCESS_TOKEN=polar_oat_QBoGv8YGoNQwMIWdEMLBk9aXYTZSN5WPVOoWt2ENnmy
POLAR_WEBHOOK_SECRET=polar_whs_h2512lJjXrj0R8hxR2q2JNZlij8MpxpimKfzq41AcrW
POLAR_PRODUCT_ID=26111cdd-7cf0-49b3-a068-61eede577684
POLAR_SUCCESS_URL=https://lohacoachpilot.onrender.com/success?checkout_id={CHECKOUT_ID}

# Existing Configuration (keep these)
GEMINI_API_KEY=your_gemini_api_key
PORT=9024
```

### 5. Deploy to Render

**Option A: Automatic Deployment (Git-based)**
1. Connect your GitHub repository to Render
2. Render will automatically deploy on push
3. Monitor deployment logs

**Option B: Manual Deployment**
1. Go to Render dashboard
2. Click "Deploy" for your service
3. Monitor deployment logs

### 6. Configure Polar Webhook

After deployment, configure the webhook in Polar.sh dashboard:

1. Log in to Polar.sh
2. Navigate to your product settings
3. Find webhook configuration section
4. Add webhook URL: `https://lohacoachpilot.onrender.com/api/polar/webhook`
5. Set webhook secret: `polar_whs_h2512lJjXrj0R8hxR2q2JNZlij8MpxpimKfzq41AcrW`
6. Enable webhook events:
   - `checkout.completed`
7. Save configuration

## Post-Deployment Verification

### 1. Basic Functionality
- [ ] App loads at https://lohacoachpilot.onrender.com
- [ ] New sessions can be created
- [ ] Messages work normally (first 6)
- [ ] No errors in browser console

### 2. Paywall Testing
- [ ] Send 6 messages (should work normally)
- [ ] Send 7th message (paywall should appear)
- [ ] Paywall displays correctly
- [ ] Payment button is visible
- [ ] Checkout URL is generated

### 3. Payment Flow
- [ ] Click payment button
- [ ] Redirected to Polar checkout
- [ ] Complete test payment
- [ ] Redirected to success page
- [ ] Success page displays correctly

### 4. Session Continuity
- [ ] Click "Return to Conversation"
- [ ] Chat interface loads
- [ ] Previous messages are visible
- [ ] Can send new messages
- [ ] No paywall appears (session is paid)

### 5. Webhook Testing
- [ ] Check Polar dashboard for webhook calls
- [ ] Verify webhook receives events
- [ ] Check server logs for webhook processing
- [ ] No errors in webhook handling

## Monitoring

### Key Metrics to Track
1. **Paywall Trigger Rate**: How often paywall appears
2. **Payment Conversion Rate**: How many users complete payment
3. **Session Continuity**: How many paid users return
4. **Error Rates**: Paywall-related errors
5. **Revenue**: Total revenue from payments

### Logs to Monitor
```
# Application logs
tail -f /var/log/app.log

# Look for:
- Polar checkout creation
- Payment webhook events
- Session payment status changes
- Paywall trigger events
```

### Common Issues and Solutions

#### Issue: Paywall Not Triggering
**Check:**
- Message counter is incrementing
- `PAYWALL_MESSAGE_LIMIT` is set to 6
- Payment status check is working

**Solution:**
- Check logs for message counter values
- Verify session_id consistency
- Test payment status function

#### Issue: Payment Not Processing
**Check:**
- Polar API credentials are correct
- Webhook URL is accessible
- Product ID matches

**Solution:**
- Verify environment variables
- Check Polar dashboard for API errors
- Test webhook endpoint manually

#### Issue: Session Lost After Payment
**Check:**
- Session_id passed through checkout URL
- Success page marks session as paid
- `paid_sessions` set is maintained

**Solution:**
- Check success page logs
- Verify session_id persistence
- Consider Redis for production

## Rollback Plan

If deployment has issues:

```bash
# Rollback to previous commit
git revert HEAD
git push origin main

# Or checkout previous commit
git checkout <previous-commit-hash>
git push origin main --force
```

## Support

### Documentation
- **Integration Guide**: `POLAR_INTEGRATION_GUIDE.md`
- **This Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Integration Summary**: `INTEGRATION_SUMMARY.md`

### External Resources
- **Polar.sh Docs**: https://docs.polar.sh/
- **Render Docs**: https://render.com/docs
- **Flask Docs**: https://flask.palletsprojects.com/

### Troubleshooting
1. Check server logs first
2. Review Polar dashboard for errors
3. Test webhook endpoint manually
4. Verify environment variables
5. Check browser console for frontend issues

## Success Criteria

Deployment is successful when:
- ✅ All tests pass (post-deployment verification)
- ✅ Paywall triggers correctly at 6 messages
- ✅ Payment flow works end-to-end
- ✅ Sessions continue after payment
- ✅ No errors in logs
- ✅ Webhook receives and processes events
- ✅ Revenue tracking works

---

## 🚀 Ready to Deploy!

All integration work is complete and tested. Follow this checklist to deploy the Polar.sh paywall to production.

**Estimated Deployment Time**: 15-20 minutes

**Critical Path**: Configure environment variables → Deploy → Configure webhook → Test