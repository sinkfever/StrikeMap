# Setup

## Authentication

> [!IMPORTANT]
> A Schwab Developer account and API crendential is needed to run the following program.

1) Create a .env file.
2) Take the template in .env.example, and replace the appropriate fields.

```
SCHWAB_APP_KEY=''
SCHWAB_APP_SECRET=''
SCHWAB_CALLBACK_URL=https://127.0.0.1
SCHWAB_TOKEN_PATH=''
```

* ```SCHWAB_APP_KEY``` and ```SCHWAB_APP_SECRET``` can be found in the developer portal for the app you create.
* ```SCHWAB_CALLBACK_URL``` must match what is set in the app page on your developer portal.
3) Run ```app.py```, then Schwab will ask to authenticate, follow the instructions opened in your browser.
4) Done!
