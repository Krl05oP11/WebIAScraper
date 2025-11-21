# LinkedIn API Integration Issue Report

**Date:** November 21, 2025  
**App Name:** WebIAScraperNewsBot  
**App ID:** Client ID: 772xf3pj1mjy19  
**Developer:** Carlos Ponce (schaller.ponce@gmail.com)

---

## Issue Summary

Unable to post to LinkedIn personal profile via `/v2/ugcPosts` API despite having "Share on LinkedIn" product approved and valid OAuth token with `w_member_social` scope.

**Error Received:**
```json
{
  "status": 403,
  "serviceErrorCode": 100,
  "code": "ACCESS_DENIED",
  "message": "Field Value validation failed in REQUEST_BODY: Data Processing Exception while processing fields [/author]"
}
```

---

## Configuration Details

### Approved Products
- ✅ **Share on LinkedIn** (Approved - provides `w_member_social` scope)
- ✅ **Sign In with LinkedIn using OpenID Connect** (Approved - provides `openid`, `profile`, `email`)

### Access Token Details
- **Scope:** `w_member_social`
- **Obtained via:** OAuth 2.0 authorization code flow
- **Status:** Valid (not expired)
- **Person URN:** `urn:li:person:27323330` and `urn:li:member:27323330` (both tested)

---

## API Request Details

### Endpoint
```
POST https://api.linkedin.com/v2/ugcPosts
```

### Headers
```
Authorization: Bearer [VALID_TOKEN]
Content-Type: application/json
X-Restli-Protocol-Version: 2.0.0
```

### Request Body (simplified)
```json
{
  "author": "urn:li:member:27323330",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Test post from API"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

---

## Troubleshooting Attempts

### ✅ Verified Configurations
1. OAuth flow completed successfully
2. Access token obtained and validated
3. Correct API endpoint used (`/v2/ugcPosts`)
4. Required headers included (`X-Restli-Protocol-Version: 2.0.0`)
5. Request body follows official documentation format

### ❌ Attempted Solutions (All Failed)

#### 1. Different URN Formats Tested
- `urn:li:person:27323330` → **Error 422**: "does not match urn:li:company:\\d+|urn:li:member:\\d+"
- `urn:li:member:27323330` → **Error 403**: ACCESS_DENIED (author field validation)

#### 2. Tried Legacy vs New API
- Legacy API: `/v2/ugcPosts` → Error 403
- New API: `/rest/posts` → Error 403

#### 3. Attempted to Obtain Additional Scopes
- Requested `r_liteprofile` via OAuth → **Error**: "unauthorized_scope_error - Scope 'r_liteprofile' is not authorized"
- Note: `r_liteprofile` appears to be deprecated

#### 4. Checked Alternative Endpoints
- `/v2/me` → **Error 403**: "Not enough permissions to access: me.GET.NO_VERSION"
- `/v2/userinfo` (OpenID Connect) → Returns alphanumeric `sub` (e.g., "6pAAJRl4XN"), not numeric ID needed

---

## Root Cause Analysis

Based on extensive research and testing:

1. **"Share on LinkedIn" product provides only `w_member_social` scope**
   - This scope alone appears insufficient for author field validation

2. **Person URN cannot be reliably obtained with available scopes**
   - `/v2/me` requires additional permissions not granted
   - `/v2/userinfo` returns incompatible alphanumeric ID
   - `r_liteprofile` and `r_basicprofile` are deprecated

3. **Circular dependency in documentation**
   - Share on LinkedIn docs reference "Sign In with LinkedIn" for Person URN
   - Sign In with LinkedIn provides OpenID scopes that don't resolve the issue
   - No clear migration path from deprecated scopes

---

## Questions for LinkedIn Support

### 1. Scope Requirements
**Q:** What exact OAuth scopes are required to successfully post to a personal profile via `/v2/ugcPosts` API?

Is `w_member_social` alone sufficient, or are additional scopes required that are no longer available via self-serve products?

### 2. Person URN Retrieval
**Q:** What is the correct method to obtain the numeric Person URN (`urn:li:person:XXXXX` or `urn:li:member:XXXXX`) with the scopes available from "Share on LinkedIn" + "Sign In with LinkedIn using OpenID Connect"?

- `/v2/me` returns 403 error
- `/v2/userinfo` returns alphanumeric `sub` value
- Are there alternative endpoints?

### 3. Product Requirements
**Q:** Do I need to apply for **Community Management API** product to enable posting to personal profiles?

If so:
- What are the specific requirements?
- Does it provide the missing scopes/permissions?
- What is the typical approval timeline?

### 4. Migration Path
**Q:** With `r_liteprofile` and `r_basicprofile` deprecated, what is the official migration path for applications that need to:
1. Authenticate a user
2. Obtain their Person URN
3. Post to their profile

---

## Use Case Description

**Application Purpose:**
Automated news aggregation and distribution service that:
- Curates AI/tech news from various sources
- Processes content with AI
- Publishes to multiple social platforms on behalf of authenticated users

**LinkedIn Integration Goal:**
- Allow users to authorize the app to post news updates to their personal LinkedIn profiles
- Posts include proper attribution, disclaimers, and source links
- Fully compliant with LinkedIn policies and terms

**Current Status:**
- Successfully posting to Telegram, Bluesky, and Twitter
- LinkedIn integration blocked by author field validation error

---

## Reference Links

### Official Documentation Reviewed
- [Share on LinkedIn](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [Sign In with LinkedIn using OpenID Connect](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2)
- [UGC Post API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/ugc-post-api)
- [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)

### Stack Overflow References
- [Field Value validation failed - author field](https://stackoverflow.com/questions/55017613/)
- [How to Get Numeric Member ID](https://stackoverflow.com/questions/79565727/)
- [v2/ugcPosts failing with person URN](https://stackoverflow.com/questions/79404448/)

---

## Request

Please provide guidance on:
1. The correct configuration to enable posting to personal profiles
2. Which product(s) need to be added to the app
3. Step-by-step instructions for obtaining the Person URN with available scopes
4. Any additional approval processes required

---

**Thank you for your assistance.**

---

**Developer Contact:**
- Email: schaller.ponce@gmail.com
- LinkedIn Profile: https://www.linkedin.com/in/carlos-onofre-ponce-27323330/
- Stack Overflow: Can provide if needed for follow-up
