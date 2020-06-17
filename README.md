# gapp-login

GINO App extension to support multiple login providers.


## SMS Login

![SMS Login](images/sms.png)

Test SMS Login with Swagger-UI.

1. Click "Authorize" in Swagger-UI.
2. In the popup, check `openid` scope.
3. Click "Authorize", a link is shown in a new tab, don't follow the link.
4. In the new tab, append `&prompt=json` to the URL in the address bar, hit ENTER and
   you'll get a JSON.
5. Copy the value of the `context` into clipboard, this is a JWT token as the login
   context.
6. In the same new tab, browse to Swagger-UI again.
7. Try out `POST /login/sms`, use the copied value as `token`, use `+86` for prefix,
   and any mobile number.
8. Hit "Execute", find the SMS ID in the result.
9. Try out `PUT /login/sms/{sms_id}`, use the previous SMS ID, the same token and
   `code` found in the server-side debug log.
10. Hit "Execute", it says "Method Not Allowed", that's okay.
11. Find the actual redirect URL in the server-side log, paste it into the address
    bar of the same new tab, leave the host name and port as it is.
12. Hit ENTER and the new tab will be closed, with the original Swagger-UI logged in.


## WeChat Login

![WeChat Login](images/wechat.png)

