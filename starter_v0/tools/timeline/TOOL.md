---
name: timeline
track: core
kind: live_api
provider: RapidAPI Twitter API45
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [screenname, limit, verify_only]
outputs: [items, account_status]
side_effect: false
---
# timeline

Fetches recent posts from a single account. `screenname` is an account handle
without `@`.
