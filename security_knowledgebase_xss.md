# Cross-Site Scripting (XSS) Knowledge Base

## What is XSS?

XSS, or Cross-Site Scripting, is a web security vulnerability that allows an attacker to inject malicious scripts into websites viewed by other users.

## Types of XSS Attacks:

*   **Reflected XSS:** The malicious script is injected through input fields (e.g., search boxes, forms) and immediately reflected back to the user without proper sanitization. This typically involves crafting a URL with the malicious script.
*   **Stored XSS:** The malicious script is permanently stored on the target server (e.g., in a database) and served to users when they access the affected page.  This is often more dangerous than reflected XSS.
*   **DOM-based XSS:** The vulnerability exists within the client-side JavaScript code itself, manipulating the Document Object Model (DOM) without proper input validation.

## How does XSS work?

1.  An attacker crafts a malicious script.
2.  The attacker injects this script into a vulnerable website through an input field or URL parameter.
3.  The vulnerable website displays the injected script to other users, who unknowingly execute it in their browsers.

## Prevention Techniques:

*   **Input Validation:** Strictly validate all user inputs on both the client-side and server-side. Reject any input that doesn't conform to expected formats or patterns.
*   **Output Encoding/Escaping:** Encode or escape data before displaying it in a web page. This converts potentially harmful characters into their safe HTML entities, preventing them from being interpreted as code.
*   **Content Security Policy (CSP):** Implement CSP headers to control the sources from which the browser is allowed to load resources (scripts, styles, etc.).
*   **Use a Web Application Firewall (WAF):** A WAF can help detect and block XSS attacks in real-time.

## Example (Reflected XSS):

Let's say a website has a search box. An attacker could craft a URL like this:

`https://example.com/search?q=<script>alert('XSS')</script>`

When a user clicks on this link, the browser will execute the JavaScript code within the `<script>` tag.

## Resources:

*   [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/Documentation/XSS_Prevention_Cheat_Sheet)
*   [Mozilla Developer Network - XSS](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Security/Cross-site_Scripting)