# HTML Injection Lab

A small, bWAPP-style educational web application for practising **reflected HTML injection (GET and POST)** with **Firefox** and **Burp Suite Community Edition**.

The application is intentionally vulnerable. Only two endpoints render user-supplied values as raw HTML: `/htmli_get.php` and `/htmli_post.php`.

> **Warning:** This lab is for local, educational use only. It is bound to `127.0.0.1` and must not be exposed to a network or the internet. Never enter real personal information.

---

## 1. Requirements

- Windows 10 / 11
- Python 3.9 or newer (tested with Python 3.13)
- Mozilla Firefox
- Burp Suite Community Edition
- Optional: FoxyProxy Standard extension for Firefox

---

## 2. Windows installation

Open **PowerShell** in the project folder (`D:\web site\html injection`) and run:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks the activation script, run this once for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Alternatively, skip the virtual environment and install Flask for the current user:

```powershell
py -m pip install -r requirements.txt
```

## 3. Run the application

With the virtual environment active:

```powershell
python app.py
```

If you installed Flask globally instead, run:

```powershell
py app.py
```

Open Firefox and browse to:

```text
http://127.0.0.1:5000
```

Press `Ctrl+C` in the terminal to stop the server.

### Laboratory credentials

| Username | Password |
| -------- | -------- |
| `bee`    | `bug`    |

---

## 4. Routes

| Route                       | Method     | Purpose                              |
| --------------------------- | ---------- | ------------------------------------ |
| `/login`                    | GET, POST  | Lab login (standard POST form)       |
| `/portal`                   | GET        | Vulnerability selection              |
| `/htmli_get.php`            | GET        | Reflected HTML injection - GET       |
| `/htmli_post.php`           | GET, POST  | Reflected HTML injection - POST      |
| `/logout`                   | GET        | Ends the session                     |

---

## 5. Burp Suite + Firefox setup

1. Start Burp Suite Community Edition and confirm **Proxy > Proxy settings** shows a listener on `127.0.0.1:8080`.
2. Configure Firefox to send traffic through Burp. Either:
   - Use FoxyProxy: add a proxy `127.0.0.1` port `8080` for the lab, or
   - Firefox **Settings > Network Settings > Settings**: Manual proxy, HTTP proxy `127.0.0.1`, port `8080`, and enable "Also use this proxy for HTTPS".
3. Install the Burp CA certificate in Firefox so HTTPS is not blocked. For this lab only HTTP is used, but the certificate is still needed if Burp is set to intercept all traffic with HTTPS sites in a separate tab.
   - Visit `http://burp` in Firefox while proxying, download the CA certificate, and import it under **Settings > Privacy & Security > Certificates > View Certificates > Authorities > Import**.
4. In Burp, open **Proxy > Intercept** and click **Intercept is off/on** as needed.
5. Set Firefox's Firefox proxy exception if desired, but do **not** add an exception for `127.0.0.1` if you want Burp to see the lab traffic. Make sure Burp's proxy is actually used for localhost (Firefox does send localhost through the configured proxy).

> Tip: Burp may capture CSS and favicon requests too. You can keep **Intercept** off until the testing page has loaded, then enable it before submitting the form. Use **Forward** for requests you do not need to modify.

---

## 6. GET experiment

1. Open `http://127.0.0.1:5000` in Firefox.
2. Log in with `bee` / `bug`. The login is a standard HTTP POST request and appears in Burp if interception is enabled.
3. On the portal, select **HTML Injection (Reflected) - GET**.
4. Turn on **Intercept** in Burp.
5. Click the **Hack** button on the portal. This sends a normal `GET /htmli_get.php` request. **Forward** it so the testing page loads.
6. Click **Go** on the testing page (sample values may be empty or filled in). Burp intercepts:
   ```http
   GET /htmli_get.php?firstname=prajwal&lastname=jogi&form=submit HTTP/1.1
   ```
7. Edit the query string in the raw request, for example:
   ```http
   GET /htmli_get.php?firstname=%3Ch1%3EInjected%3C%2Fh1%3E&lastname=%3Cb%3Ejogi%3C%2Fb%3E&form=submit HTTP/1.1
   ```
   Use Burp's `Ctrl+U` (URL-encode) after typing special characters so the parameters remain valid URL-encoded form data.
8. **Forward** the request and inspect the HTML response in Burp or in Firefox. The injected markup is rendered raw in the result area.

Alternative: if intercept is enabled *before* clicking **Hack**, forward the initial page-load request, then submit the form to intercept the subsequent GET with the parameters.

## 7. POST experiment

1. Log in at `http://127.0.0.1:5000` (if not already logged in).
2. On the portal, select **HTML Injection (Reflected) - POST**.
3. Enter a first name and last name on the testing page.
4. Turn on **Intercept** in Burp.
5. Click **Go**. Burp intercepts a standard POST request:
   ```http
   POST /htmli_post.php HTTP/1.1
   Content-Type: application/x-www-form-urlencoded
   Content-Length: 43

   firstname=prajwal&lastname=jogi&form=submit
   ```
6. Modify the request body, for example:
   ```text
   firstname=%3Ch1%3EInjected%3C%2Fh1%3E&lastname=%3Cb%3Ejogi%3C%2Fb%3E&form=submit
   ```
   Keep the `Content-Length` header consistent (Burp updates it automatically when you edit the body, or use **Update Content-Length** in Repeater).
7. **Forward** the request and observe the modified HTML output.

## 8. Example payloads

Submit these through Burp (URL-encode them in the raw request) or directly through the on-page form:

```html
<h1>Injected heading</h1>
<b>bold injection</b>
<a href="https://example.com">Injected link</a>
<img src=x alt="injected image">
<marquee>HTML injection</marquee>
<iframe src="https://example.com" width="400" height="200"></iframe>
```

For a JavaScript-execution demonstration:

```html
<script>alert('HTML Injection')</script>
<img src=x onerror=alert('HTML Injection')>
```

A browser may block some of these depending on settings and payload context, but the raw markup is still visible in the HTTP response and in the rendered page. This exercise focuses on **reflected HTML injection through interceptable HTTP requests**.

> When editing raw HTTP requests in Burp, special characters must be URL-encoded. Select the value and press `Ctrl+U`, or type the already-encoded payload shown above.

## 9. How the lab is built

| File                       | Purpose                                              |
| -------------------------- | ---------------------------------------------------- |
| `app.py`                   | Flask application, authentication, lab endpoints     |
| `templates/base.html`      | Shared layout and navigation                         |
| `templates/login.html`     | Login form                                           |
| `templates/portal.html`    | Vulnerability selection with Hack buttons            |
| `templates/htmli_get.html` | GET testing page and raw result rendering             |
| `templates/htmli_post.html`| POST testing page and raw result rendering            |
| `static/style.css`         | bWAPP-style white/blue interface                     |
| `requirements.txt`         | Python dependency                                    |

Implementation notes:

- Login, portal, and both labs use ordinary HTML forms and standard GET/POST requests.
- No Fetch API, AJAX, or JavaScript form submission is used.
- The `firstname` and `lastname` values are deliberately rendered with Jinja's `|safe` filter **only** in `htmli_get.html` and `htmli_post.html`.
- Every other template relies on Jinja autoescaping.
- HTML responses are sent with `Cache-Control: no-store` so each experiment produces a fresh request.
- The server binds to `127.0.0.1` and does not use Flask debug mode.

## 10. Isolation and safety

- Run the server only on `127.0.0.1:5000`. Do not change the host to `0.0.0.0`.
- Do not expose the lab through port forwarding, tunnels, or reverse proxies.
- Use only the fictional credentials and fake data supplied in this lab.
- Do not browse other sites through the same intercepting proxy session while testing untrusted payloads.
- This lab intentionally disables output escaping only for the two HTML injection endpoints. Treat it as a deliberately vulnerable training target.

---

## 11. Troubleshooting

| Problem | Check |
| ------- | ----- |
| Firefox cannot reach the site | Make sure `python app.py` (or `py app.py`) is still running and visit `http://127.0.0.1:5000` directly. |
| Burp does not see lab requests | Confirm Firefox is using the `127.0.0.1:8080` proxy and Burp's listener is on the same address/port. Firefox proxies localhost requests by default. |
| Port 5000 is already in use | Stop the other process, or edit the port in `app.py` (and update this README). |
| Burp shows a certificate error | Install the Burp CA certificate in Firefox. This lab itself uses HTTP, but other intercepted pages may be HTTPS. |
| Injected markup appears as text | Ensure `|safe` is present in the testing template, and verify you forwarded the modified request rather than the original. |
| POST body is empty in Burp | Confirm the request uses `Content-Type: application/x-www-form-urlencoded` and that the form was submitted with the POST method. |
| Lab pages redirect to the login page | Log in first and preserve the session cookie. Restarting the Flask server invalidates old sessions. |
| `py` is not recognized | Install Python from python.org and enable the Python Launcher during installation. |

---

## 12. Clean shutdown

Stop the Flask server with `Ctrl+C`, turn off Burp interception, and remove the Firefox proxy settings when you are finished.