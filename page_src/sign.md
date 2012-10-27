# START AUTHORIZATION

<div class="authform">
<form action="/oauth/request_token" method="get">
Invitation code: <input type="text" size="9" name="code">
<input type="submit" value="Start Authorization">
<div class="badauth">
{{error_msg}}
</div>
</form>
</div>

* This page will direct you to twitter authorization page.
* In the twitter authorization page you will find a detailed list of permissions twig are asking for. 
* Login and click "Authorize app" to continue **if you trust** the administrator of `{{app_name}}.appspot.com`
* After that you will be redirected back to twig, and an access token will be generated and stored in twig.

> twig will store **nothing more than your access token and custom settings.**
> Although access token enables twig to access your timeline, mentions, etc. and send tweets, it has **nothing to do with your password**.
> you can revoke access to twig at any time from the [Applications tab](www.twitter.com/settings/applications) of your settings page.

