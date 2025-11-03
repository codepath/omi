# Testing Stripe Promotion Codes Integration

## Summary

Stripe promotion codes have been successfully enabled in the Omi backend. This guide will help you verify the functionality works correctly.

## Changes Made

### 1. Backend Configuration ✅
**File:** `backend/utils/stripe.py`
- Added `allow_promotion_codes=True` to the `create_subscription_checkout_session` function
- This enables users to enter promotion/discount codes during checkout

### 2. App Configuration ✅
**File:** `app/.dev.env`
- Updated `API_BASE_URL` to use public backend: `https://api.omiapi.com/`
- Allows testing without local backend setup

## Automated Tests

We've created a test suite to verify the changes. To run:

```bash
cd backend
python test_stripe_promotion_codes.py
```

**Test Results:**
- ✅ Code review: `allow_promotion_codes=True` correctly added
- ✅ Structure check: All required fields present in checkout session

## Manual Testing Guide

### Option 1: Test with Omi Mobile App

1. **Build and run the app:**
   ```bash
   cd app
   flutter run --flavor dev
   ```

2. **Navigate to subscription page:**
   - Log in to the app
   - Go to Settings > Usage
   - Tap "Upgrade to Unlimited"

3. **Verify promotion code field:**
   - When the Stripe checkout page opens in the browser
   - Look for a "Promotion code" or "Have a code?" link/field
   - Click on it to expand the promotion code input

4. **Test with a valid promotion code:**
   - Create a test promotion code in your Stripe Dashboard:
     - Go to Products > Coupons (or Promotion Codes)
     - Create a new promotion code (e.g., "TEST20" with 20% off)
   - Enter the code in the checkout
   - Verify the discount is applied and the final price updates

### Option 2: Test via API directly

1. **Start your local backend** (optional, or use public API):
   ```bash
   cd backend
   uvicorn main:app --reload --env-file .env
   ```

2. **Create a checkout session:**
   ```bash
   curl -X POST https://api.omiapi.com/v1/payments/checkout-session \
     -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"price_id": "YOUR_STRIPE_PRICE_ID"}'
   ```

3. **Open the returned URL in a browser** to see the checkout page with promotion code field

### Option 3: Inspect Checkout Session in Stripe Dashboard

1. Go to your [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Developers > Events**
3. Look for `checkout.session.created` events
4. Click on an event to see the session details
5. Verify that `allow_promotion_codes: true` is present in the API call

## Expected Behavior

### Before the Change ❌
- No promotion code field in Stripe checkout
- Users cannot apply discounts
- All checkouts processed at full price

### After the Change ✅
- Promotion code field visible in Stripe checkout
- Users can enter valid codes
- Discounts automatically applied
- Checkout shows discounted pricing

## Troubleshooting

### Issue: Promotion code field not appearing

**Possible causes:**
1. App not using the updated backend
   - Check `app/.dev.env` has correct `API_BASE_URL`
   - Regenerate environment files: `dart run build_runner build --delete-conflicting-outputs`
   
2. Backend not deployed with changes
   - Verify `backend/utils/stripe.py` has `allow_promotion_codes=True`
   - If using public API, wait for deployment or test locally

3. Browser cache
   - Try incognito/private mode
   - Clear browser cache and cookies

### Issue: Promotion code not working

**Possible causes:**
1. Invalid or expired code
   - Check code is active in Stripe Dashboard
   - Verify code hasn't reached usage limits
   
2. Code restrictions
   - Some codes may be restricted by customer, country, or product
   - Create test codes with minimal restrictions

3. Price compatibility
   - Ensure code works with subscription prices (not one-time payments)

## Verification Checklist

- [ ] Test suite passes: `python backend/test_stripe_promotion_codes.py`
- [ ] Promotion code field appears in checkout
- [ ] Can enter a promotion code
- [ ] Valid code applies discount correctly
- [ ] Invalid code shows error message
- [ ] Final price reflects discount
- [ ] Subscription created successfully with discount

## Next Steps

After successful testing:

1. **Commit the changes:**
   ```bash
   git add backend/utils/stripe.py app/.dev.env
   git commit -m "feat: enable promotion codes in Stripe checkout"
   ```

2. **Deploy to production** (when ready):
   - Update backend with the new code
   - Verify production environment variables are set

3. **Create production promotion codes** in Stripe Dashboard for marketing campaigns

## Files Modified

1. `backend/utils/stripe.py` - Added `allow_promotion_codes=True`
2. `app/.dev.env` - Updated `API_BASE_URL` to public backend
3. `backend/test_stripe_promotion_codes.py` - Created test suite

## Additional Resources

- [Stripe Promotion Codes Documentation](https://stripe.com/docs/billing/subscriptions/discounts/codes)
- [Stripe Checkout API Reference](https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-allow_promotion_codes)
- [Omi Backend Setup](backend/README.md)
